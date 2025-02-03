# Azure Maps Weather Package client library for Python

This package contains a Python SDK for Azure Maps Services for Weather.
Read more about Azure Maps Services [here](https://learn.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-weather) | [API reference documentation](https://learn.microsoft.com/rest/api/maps/weather) | [Product documentation](https://learn.microsoft.com/azure/azure-maps/)

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

Install the Azure Maps Service Weather SDK.

```bash
pip install azure-maps-weather
```

### Create and Authenticate the MapsWeatherClient

To create a client object to access the Azure Maps Weather API, you will need a **credential** object. Azure Maps Weather client also support two ways to authenticate.

#### 1. Authenticate with a Subscription Key Credential

You can authenticate with your Azure Maps Subscription Key.
Once the Azure Maps Subscription Key is created, set the value of the key as environment variable: `AZURE_SUBSCRIPTION_KEY`.
Then pass an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter into an instance of [AzureKeyCredential][azure-key-credential].

```python
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.weather import MapsWeatherClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))

maps_weather_client = MapsWeatherClient(
    credential=credential,
)
```

#### 2. Authenticate with an Microsoft Entra ID credential

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
from azure.maps.weather import MapsWeatherClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
weather_client = MapsWeatherClient(credential=credential)
```

## Key concepts

The Azure Maps Weather client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsWeatherClient` is the primary client for developers using the Azure Maps Weather client library for Python.
Once you initialized a `MapsWeatherClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Weather service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.8+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Weather tasks, including:
- [Get air quality daily forecasts](#get-air-quality-daily-forecasts)
- [Get air quality hourly forecasts](#get-air-quality-hourly-forecasts)
- [Get current air quality](#get-current-air-quality)
- [Get current conditions](#get-current-conditions)
- [Get daily forecast](#get-daily-forecast)
- [Get daily historical actuals](#get-daily-historical-actuals)
- [Get daily historical normals](#get-daily-historical-normals)
- [Get daily historical records](#get-daily-historical-records)
- [Get daily indices](#get-daily-indices)
- [Get hourly forecast](#get-hourly-forecast)
- [Get minute forecast](#get-minute-forecast)
- [Get quarter day forecast](#get-quarter-day-forecast)
- [Get severe weather alerts](#get-severe-weather-alerts)
- [Get tropical storm active](#get-tropical-storm-active)
- [Get tropical storm forecast](#get-tropical-storm-forecast)
- [Get tropical storm locations](#get-tropical-storm-locations)
- [Get tropical storm search](#get-tropical-storm-search)
- [Get weather along route](#get-weather-along-route)

### Get air quality daily forecasts

This API returns daily air quality forecasts for the next one to seven days that include pollutant levels, potential risks and suggested precautions.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_air_quality_daily_forecasts():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_air_quality_daily_forecasts(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_air_quality_daily_forecasts()
```

### Get air quality hourly forecasts

This API returns hourly air quality forecasts for the next one to 96 hours that include pollutant levels, potential risks and suggested precautions.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_air_quality_hourly_forecasts():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_air_quality_hourly_forecasts(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_air_quality_hourly_forecasts()
```

### Get current air quality

This API returns current air quality information that includes potential risks and suggested precautions.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_current_air_quality():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_current_air_quality(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_current_air_quality()
```

### Get current conditions

This API returns current weather conditions.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_current_conditions():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_current_conditions(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_current_conditions()
```

### Get daily forecast

This API returns a daily detailed weather forecast for the next 1, 5, 10, 15, 25, or 45 days.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_daily_forecast():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_forecast(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_daily_forecast()
```

### Get daily historical actuals

This API returns climatology data such as past daily actual observed temperatures, precipitation, snowfall and snow depth.

```python
import os
import json
import datetime

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_daily_historical_actuals():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_historical_actuals(
            coordinates=[40.760139, -73.961968],
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_daily_historical_actuals()
```

### Get daily historical normals

This API returns climatology data such as past daily normal temperatures, precipitation and cooling/heating degree day information for a given location.

```python
import os
import json
import datetime

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_daily_historical_normals():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_historical_normals(
            coordinates=[40.760139, -73.961968],
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_daily_historical_normals()
```

### Get daily historical records

This API returns climatology data such as past daily record temperatures, precipitation and snowfall at a given location.

```python
import os
import json
import datetime

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_daily_historical_records():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_historical_records(
            coordinates=[40.760139, -73.961968],
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_daily_historical_records()
```

### Get daily indices

This API returns if the weather conditions are optimal for a specific activity such as outdoor sporting activities, construction, or farming.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_daily_indices():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_indices(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_daily_indices()
```

### Get hourly forecast

This API returns a detailed hourly weather forecast for up to 24 hours or a daily forecast for up to 10 days.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_hourly_forecast():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_hourly_forecast(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_hourly_forecast()
```

### Get minute forecast

This API returns a minute-by-minute forecast for the next 120 minutes in intervals of 1, 5 and 15 minutes.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_minute_forecast():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_minute_forecast(coordinates=[25.0338053, 121.5640089])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_minute_forecast()
```

### Get quarter day forecast

This API returns a Quarter-Day Forecast for the next 1, 5, 10, or 15 days.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_quarter_day_forecast():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_quarter_day_forecast(coordinates=[39.793451, -104.944511])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_quarter_day_forecast()
```

### Get severe weather alerts

This API returns information about severe weather conditions such as hurricanes, thunderstorms, flooding, lightning, heat waves or forest fires for a given location.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_severe_weather_alerts():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_severe_weather_alerts(coordinates=[39.793451, -104.944511])
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_severe_weather_alerts()
```

### Get tropical storm active

This API returns a list of the active tropical storms issued by national weather forecasting agencies.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_tropical_storm_active():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_tropical_storm_active()
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_tropical_storm_active()
```

### Get tropical storm forecast

This API returns a list of tropical storms forecasted by national weather forecasting agencies.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_tropical_storm_forecast():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_tropical_storm_forecast(
            year=2021,
            basin_id="NP",
            government_storm_id=2
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_tropical_storm_forecast()
```

### Get tropical storm locations

This API returns the location of tropical storms from individual national weather forecasting agencies.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_tropical_storm_locations():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_tropical_storm_locations(
            year=2021,
            basin_id="NP",
            government_storm_id=2
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_tropical_storm_locations()
```

### Get tropical storm search

This API returns a list of storms issued by national weather forecasting agencies.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_tropical_storm_search():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_tropical_storm_search(year=2022)
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_tropical_storm_search()
```

### Get weather along route

This API returns a locationally precise, up-to-the-minute forecast that includes weather hazard assessments and notifications along a route.

```python
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_weather_along_route():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_weather_along_route(
            query='25.033075,121.525694,0:25.0338053,121.5640089,2'
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_weather_along_route()
```

## Troubleshooting

### General

Maps Weather clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

This list can be used for reference to catch thrown exceptions. To get the specific error code of the exception, use the `error_code` attribute, i.e, `exception.error_code`.

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
import sys
import logging

# Create a logger for the 'azure.maps.weather' SDK
logger = logging.getLogger('azure.maps.weather')
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

Get started with our [Maps Weather samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-weather/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-weather/samples/async_samples)).

Several Azure Maps Weather Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Weather.

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-weather --pre

python samples/get_air_quality_daily_forecasts.py
python samples/get_air_quality_hourly_forecasts.py
python samples/get_current_air_quality.py
python samples/get_current_conditions.py
python samples/get_daily_forecast.py
python samples/get_daily_historical_actuals.py
python samples/get_daily_historical_normals.py
python samples/get_daily_historical_records.py
python samples/get_daily_indices.py
python samples/get_hourly_forecast.py
python samples/get_minute_forecast.py
python samples/get_quarter_day_forecast.py
python samples/get_severe_weather_alerts.py
python samples/get_tropical_storm_active.py
python samples/get_tropical_storm_forecast.py
python samples/get_tropical_storm_locations.py
python samples/get_tropical_storm_search.py
python samples/get_weather_along_route.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-weather/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Weather, see the [Azure Maps Weather documentation](https://learn.microsoft.com/rest/api/maps/weather) on learn.microsoft.com.

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
