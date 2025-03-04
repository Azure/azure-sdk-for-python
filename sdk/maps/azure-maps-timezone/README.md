# Azure Maps Timezone Package client library for Python

This package contains a Python SDK for Azure Maps Services for Timezone.
Read more about Azure Maps Services [here](https://learn.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone) | [API reference documentation](https://learn.microsoft.com/rest/api/maps/timezone) | [Product documentation](https://learn.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.8 or later is required to use this package.
- An [Azure subscription][azure_subscription] and an [Azure Maps account](https://learn.microsoft.com/azure/azure-maps/how-to-manage-account-keys).
- A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

If you use Azure CLI, replace `<resource-group-name>` and `<account-name>` of your choice, and select a proper [pricing tier](https://learn.microsoft.com/azure/azure-maps/choose-pricing-tier) based on your needs via the `<sku-name>` parameter. Please refer to [this page](https://learn.microsoft.com/cli/azure/maps/account?view=azure-cli-latest#az_maps_account_create) for more details.

```bash
az maps account create --resource-group <resource-group-name> --account-name <account-name> --sku <sku-name>
```

### Install the package

Install the Azure Maps Service Timezone SDK.

```bash
pip install azure-maps-timezone
```

### Create and Authenticate the MapsTimeZoneClient

To create a client object to access the Azure Maps Timezone API, you will need a **credential** object. Azure Maps Timezone client also support three ways to authenticate.

#### 1. Authenticate with a Subscription Key Credential

You can authenticate with your Azure Maps Subscription Key.
Once the Azure Maps Subscription Key is created, set the value of the key as environment variable: `AZURE_SUBSCRIPTION_KEY`.
Then pass an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter into an instance of [AzureKeyCredential][azure-key-credential].

```python
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.timezone import MapsTimeZoneClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))

timezone_client = MapsTimeZoneClient(
    credential=credential,
)
```

#### 2. Authenticate with a SAS Credential

Shared access signature (SAS) tokens are authentication tokens created using the JSON Web token (JWT) format and are cryptographically signed to prove authentication for an application to the Azure Maps REST API.

To authenticate with a SAS token in Python, you'll need to generate one using the azure-mgmt-maps package. 

We need to tell user to install `azure-mgmt-maps`: `pip install azure-mgmt-maps`

Here's how you can generate the SAS token using the list_sas method from azure-mgmt-maps:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.maps import AzureMapsManagementClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-maps
# USAGE
    python account_list_sas.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = AzureMapsManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id="your-subscription-id",
    )

    response = client.accounts.list_sas(
        resource_group_name="myResourceGroup",
        account_name="myMapsAccount",
        maps_account_sas_parameters={
            "expiry": "2017-05-24T11:42:03.1567373Z",
            "maxRatePerSecond": 500,
            "principalId": "your-principal-id",
            "regions": ["eastus"],
            "signingKey": "primaryKey",
            "start": "2017-05-24T10:42:03.1567373Z",
        },
    )
    print(response)
```

Once the SAS token is created, set the value of the token as environment variable: `AZURE_SAS_TOKEN`.
Then pass an `AZURE_SAS_TOKEN` as the `credential` parameter into an instance of AzureSasCredential.

```python
import os

from azure.core.credentials import AzureSASCredential
from azure.maps.timezone import MapsTimeZoneClient

credential = AzureSASCredential(os.environ.get("AZURE_SAS_TOKEN"))

timezone_client = MapsTimeZoneClient(
    credential=credential,
)
```

#### 3. Authenticate with an Microsoft Entra ID credential

You can authenticate with [Microsoft Entra ID credential][maps_authentication_ms_entra_id] using the [Azure Identity library][azure_identity].
Authentication by using Microsoft Entra ID requires some initial setup:

- Install [azure-identity][azure-key-credential]
- Register a [new Microsoft Entra ID application][register_ms_entra_id_app]
- Grant access to Azure Maps by assigning the suitable role to your service principal. Please refer to the [Manage authentication page][manage_ms_entra_id_auth_page].

After setup, you can choose which type of [credential][azure-key-credential] from `azure.identity` to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Next, set the values of the client ID, tenant ID, and client secret of the Microsoft Entra ID application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

You will also need to specify the Azure Maps resource you intend to use by specifying the `clientId` in the client options. The Azure Maps resource client id can be found in the Authentication sections in the Azure Maps resource. Please refer to the [documentation][how_to_manage_authentication] on how to find it.

```python
import os
from azure.maps.timezone import MapsTimeZoneClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
timezone_client = MapsTimeZoneClient(credential=credential)
```

## Key concepts

The Azure Maps Timezone client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsTimeZoneClient` is the primary client for developers using the Azure Maps Timezone client library for Python.
Once you initialized a `MapsTimeZoneClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Timezone service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.8+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Timezone tasks, including:

- [Get timezone by id](#get-timezone-by-id)
- [Get timezone by coordinates](#get-timezone-by-coordinates)
- [Get iana version](#get-iana-version)
- [Get iana timezone ids](#get-iana-timezone-ids)
- [Get windows timezone ids](#get-windows-timezone-ids)
- [Convert windows timezone to iana](#convert-windows-timezone-to-iana)

### Get timezone by id

This API returns current, historical, and future time zone information for the specified IANA time zone ID.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_timezone_by_id():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_timezone_by_id(timezone_id="sr-Latn-RS")
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_timezone_by_id()
```

### Get timezone by coordinates

This API returns current, historical, and future time zone information for a specified latitude-longitude pair.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_timezone_by_coordinates():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_timezone_by_coordinates(coordinates=[25.0338053, 121.5640089])
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_timezone_by_coordinates()
```

### Get iana version

This API returns the current IANA version number as Metadata.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_iana_version():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_iana_version()
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_iana_version()
```

### Get iana timezone ids

This API returns a full list of IANA time zone IDs. Updates to the IANA service will be reflected in the system within one day.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_iana_timezone_ids():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_iana_timezone_ids()
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_iana_timezone_ids()
```

### Get windows timezone ids

This API returns a full list of Windows time zone IDs.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_windows_timezone_ids():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_windows_timezone_ids()
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_windows_timezone_ids()
```
### Convert windows timezone to iana

This API returns a corresponding IANA ID, given a valid Windows Time Zone ID.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def convert_windows_timezone_to_iana():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.convert_windows_timezone_to_iana(windows_timezone_id="Pacific Standard Time")
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    convert_windows_timezone_to_iana()
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

# Create a logger for the 'azure.maps.timezone' SDK
logger = logging.getLogger('azure.maps.timezone')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:

```python
service_client.get_service_stats(logging_enable=True)
```

### Additional

Still running into issues? If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

## Next steps

### More sample code

Get started with our [Maps Timezone samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples/async_samples)).

Several Azure Maps Timezone Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Timezone

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-timezone --pre

python samples/get_timezone_by_id.py
python sample/get_timezone_by_coordinates.py
python samples/get_iana_version.py
python samples/get_iana_timezone_ids.py
python samples/get_windows_timezone_ids.py
python samples/convert_windows_timezone_to_iana.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Timezone, see the [Azure Maps Timezone documentation](https://learn.microsoft.com/rest/api/maps/timezone) on learn.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[azure_portal]: https://portal.azure.com
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[register_ms_entra_id_app]: https://learn.microsoft.com/powershell/module/Az.Resources/New-AzADApplication?view=azps-8.0.0
[maps_authentication_ms_entra_id]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication
[create_new_application_registration]: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/applicationsListBlade/quickStartType/AspNetWebAppQuickstartPage/sourceType/docs
[manage_ms_entra_id_auth_page]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication
[how_to_manage_authentication]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication#view-authentication-details
