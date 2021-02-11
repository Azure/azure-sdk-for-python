[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Communication Phone Numbers Package client library for Python

Azure Communication Phone Numbers client package is used to administer Phone Numbers. 

# Getting started
### Prerequisites
- Python 2.7, or 3.5 or later is required to use this package.
- You must have an [Azure subscription](https://azure.microsoft.com/free/)
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
### Install the package
Install the Azure Communication Phone Numbers client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-phonenumbers
```

# Key concepts

## CommunicationPhoneNumberClient
### Initializing Phone Numbers Client
```python
# You can find your endpoint and access token from your resource in the Azure Portal
import os
from azure.communication.phonenumbers import PhoneNumbersAdministrationClient
from azure.identity import DefaultAzureCredential

endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have your
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
phone_number_administration_client = PhoneNumbersAdministrationClient(endpoint, DefaultAzureCredential())

```
### Initializing Phone Numbers Client Using Connection String
Connection string authentication is also available for Phone Numbers Client.

```python
# You can find your endpoint and access token from your resource in the Azure Portal
import os
from azure.communication.phonenumbers import PhoneNumbersAdministrationClient

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)
```

### Phone plans overview

Phone plans come in two types; Geographic and Toll-Free. Geographic phone plans are phone plans associated with a location, whose phone numbers' area codes are associated with the area code of a geographic location. Toll-Free phone plans are phone plans not associated location. For example, in the US, toll-free numbers can come with area codes such as 800 or 888.

All geographic phone plans within the same country are grouped into a phone plan group with a Geographic phone number type. All Toll-Free phone plans within the same country are grouped into a phone plan group.

### Reserving and Acquiring numbers

Phone numbers can be reserved through the begin_reserve_phone_numbers API by providing a phone plan id, an area code and quantity of phone numbers. The provided quantity of phone numbers will be reserved for ten minutes. This reservation of phone numbers can either be cancelled or purchased. If the reservation is cancelled, then the phone numbers will become available to others. If the reservation is purchased, then the phone numbers are acquired for the Azure resources.

### Configuring / Assigning numbers

Phone numbers can be assigned to a callback URL via the configure number API. As part of the configuration, you will need an acquired phone number, callback URL and application id.

# Examples
The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

## Communication Phone number
### Get Countries

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

supported_countries = phone_number_administration_client.list_all_supported_countries()
for supported_country in supported_countries:
    print(supported_country)
```

### Get Phone Plan Groups

Phone plan groups come in two types, Geographic and Toll-Free.

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

phone_plan_groups_response = phone_number_administration_client.list_phone_plan_groups(
    country_code='<country code>'
)
for phone_plan_group in phone_plan_groups_response:
    print(phone_plan_group)
```

### Get Phone Plans

Unlike Toll-Free phone plans, area codes for Geographic Phone Plans are empty. Area codes are found in the Area Codes API.

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

phone_plans_response = phone_number_administration_client.list_phone_plans(
    country_code='<country code>',
    phone_plan_group_id='<phone plan group id>'
)
for phone_plan in phone_plans_response:
    print(phone_plan)
```

### Get Location Options

For Geographic phone plans, you can query the available geographic locations. The locations options are structured like the geographic hierarchy of a country. For example, the US has states and within each state are cities.

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

location_options_response = phone_number_administration_client.get_phone_plan_location_options(
    country_code='<country code>',
    phone_plan_group_id='<phone plan group id>',
    phone_plan_id='<phone plan id>'
)
print(location_options_response)
```

### Get Area Codes

Fetching area codes for geographic phone plans will require the the location options queries set. You must include the chain of geographic locations traversing down the location options object returned by the GetLocationOptions API.

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

all_area_codes = phone_number_administration_client.get_all_area_codes(
    location_type="NotRequired",
    country_code='<country code>',
    phone_plan_id='<phone plan id>'
)
print(all_area_codes)
```

### Create Reservation

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

poller = phone_number_administration_client.begin_reserve_phone_numbers(
    area_code='<area code>',
    description="testreservation20200014",
    display_name="testreservation20200014",
    phone_plan_ids=['<phone plan id>'],
    quantity=1
)
```

### Get Reservation By Id
```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

phone_number_reservation_response = phone_number_administration_client.get_reservation_by_id(
    reservation_id='<reservation id>'
)
print(reservation_id)
```

### Purchase Reservation

```python
phone_number_administration_client = PhoneNumbersAdministrationClient.from_connection_string(connection_str)

poller = phone_number_administration_client.begin_purchase_reservation(
    reservation_id='<reservation id to purchase>'
)
```

# Troubleshooting
The Phone Numbers Administration client will raise exceptions defined in [Azure Core][azure_core].

# Next steps
## More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/communication/azure-communication-phonenumbers/samples) directory for detailed examples of how to use this library.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

# Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
