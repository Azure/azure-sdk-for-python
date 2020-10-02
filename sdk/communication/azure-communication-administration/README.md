[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Communication Administration Package client library for Python

Azure Communication Administration client package is intended to be used to setup the basics for opening a way to use Azure Communication Service offerings. This package helps to create identities user tokens to be used by other client packages such as chat, calling, sms. 

# Getting started
### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/)

### Install the package
Install the Azure Communication Administration client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-administration
```

# Key concepts
## CommunicationIdentityClient
`CommunicationIdentityClient` provides operations for:

- Create/delete identities to be used in Azure Communication Services. Those identities can be used to make use of Azure Communication offerings and can be scoped to have limited abilities through token scopes.

- Create/revoke scoped user access tokens to access services such as chat, calling, sms. Tokens are issued for a valid Azure Communication identity and can be revoked at any time.

## CommunicationPhoneNumberClient
### Initializing Phone Number Client
```python
# You can find your endpoint and access token from your resource in the Azure Portal
import os
from azure.communication.administration import PhoneNumberAdministrationClient

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
```
### Phone plans overview

Phone plans come in two types; Geographic and Toll-Free. Geographic phone plans are phone plans associated with a location, whose phone numbers' area codes are associated with the area code of a geographic location. Toll-Free phone plans are phone plans not associated location. For example, in the US, toll-free numbers can come with area codes such as 800 or 888.

All geographic phone plans within the same country are grouped into a phone plan group with a Geographic phone number type. All Toll-Free phone plans within the same country are grouped into a phone plan group.

### Searching and Acquiring numbers

Phone numbers search can be search through the search creation API by providing a phone plan id, an area code and quantity of phone numbers. The provided quantity of phone numbers will be reserved for ten minutes. This search of phone numbers can either be cancelled or purchased. If the search is cancelled, then the phone numbers will become available to others. If the search is purchased, then the phone numbers are acquired for the Azure resources.

### Configuring / Assigning numbers

Phone numbers can be assigned to a callback URL via the configure number API. As part of the configuration, you will need an acquired phone number, callback URL and application id.

# Examples
The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

[Create/delete Azure Communication Service identities][identitysamples] 

[Create/revoke scoped user access tokens][identitysamples]

##Communication Phone number
### Get Countries

```python
def list_all_supported_countries():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    
    supported_countries = phone_number_administration_client.list_all_supported_countries()
    for supported_country in supported_countries:
        print(supported_country)
```

### Get Phone Plan Groups

Phone plan groups come in two types, Geographic and Toll-Free.

```python
def list_phone_plan_groups():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")

    phone_plan_groups_response = phone_number_administration_client.list_phone_plan_groups(
        country_code=country_code
    )
    for phone_plan_group in phone_plan_groups_response:
        print(phone_plan_group)
```

### Get Phone Plans

Unlike Toll-Free phone plans, area codes for Geographic Phone Plans are empty. Area codes are found in the Area Codes API.

```python
def list_phone_plans():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
   
    phone_plans_response = phone_number_administration_client.list_phone_plans(
        country_code=country_code,
        phone_plan_group_id=phone_plan_group_id
    )
    for phone_plan in phone_plans_response:
        print(phone_plan)
```

### Get Location Options

For Geographic phone plans, you can query the available geographic locations. The locations options are structured like the geographic hierarchy of a country. For example, the US has states and within each state are cities.

```python
def get_phone_plan_location_options():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
    phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")

    location_options_response = phone_number_administration_client.get_phone_plan_location_options(
        country_code=country_code,
        phone_plan_group_id=phone_plan_group_id,
        phone_plan_id=phone_plan_id
    )
    print(location_options_response)
```

### Get Area Codes

Fetching area codes for geographic phone plans will require the the location options queries set. You must include the chain of geographic locations traversing down the location options object returned by the GetLocationOptions API.

```python
def get_all_area_codes():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_id_area_codes = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID_AREA_CODES', "phone-plan-id")

    all_area_codes = phone_number_administration_client.get_all_area_codes(
        location_type="NotRequired",
        country_code=country_code,
        phone_plan_id=phone_plan_id_area_codes
    )
    print(all_area_codes)
```

### Create Search

```python
def create_search():
    from azure.communication.administration import CreateSearchOptions
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")
    area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_SEARCH', "area-code")

    searchOptions = CreateSearchOptions(
        area_code=area_code_for_search,
        description="testsearch20200014",
        display_name="testsearch20200014",
        phone_plan_ids=[phone_plan_id],
        quantity=1
    )
    search_response = phone_number_administration_client.begin_create_search(
        body=searchOptions
    )
    print(search_response.status())
```

### Get search by id
```python
def get_search_by_id():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID', "search-id")

    phone_number_search_response = phone_number_administration_client.get_search_by_id(
        search_id=search_id
    )
    print(phone_number_search_response)
```

### Purchase Search

```python
def purchase_search():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_PURCHASE', "search-id")

    phone_number_administration_client.begin_purchase_search(
        search_id=search_id_to_purchase
    )
```

##Communication Phone number
### Get Countries

```python
def list_all_supported_countries():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    
    supported_countries = phone_number_administration_client.list_all_supported_countries()
    for supported_country in supported_countries:
        print(supported_country)
```

### Get Phone Plan Groups

Phone plan groups come in two types, Geographic and Toll-Free.

```python
def list_phone_plan_groups():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")

    phone_plan_groups_response = phone_number_administration_client.list_phone_plan_groups(
        country_code=country_code
    )
    for phone_plan_group in phone_plan_groups_response:
        print(phone_plan_group)
```

### Get Phone Plans

Unlike Toll-Free phone plans, area codes for Geographic Phone Plans are empty. Area codes are found in the Area Codes API.

```python
def list_phone_plans():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
   
    phone_plans_response = phone_number_administration_client.list_phone_plans(
        country_code=country_code,
        phone_plan_group_id=phone_plan_group_id
    )
    for phone_plan in phone_plans_response:
        print(phone_plan)
```

### Get Location Options

For Geographic phone plans, you can query the available geographic locations. The locations options are structured like the geographic hierarchy of a country. For example, the US has states and within each state are cities.

```python
def get_phone_plan_location_options():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
    phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")

    location_options_response = phone_number_administration_client.get_phone_plan_location_options(
        country_code=country_code,
        phone_plan_group_id=phone_plan_group_id,
        phone_plan_id=phone_plan_id
    )
    print(location_options_response)
```

### Get Area Codes

Fetching area codes for geographic phone plans will require the the location options queries set. You must include the chain of geographic locations traversing down the location options object returned by the GetLocationOptions API.

```python
def get_all_area_codes():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
    phone_plan_id_area_codes = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID_AREA_CODES', "phone-plan-id")

    all_area_codes = phone_number_administration_client.get_all_area_codes(
        location_type="NotRequired",
        country_code=country_code,
        phone_plan_id=phone_plan_id_area_codes
    )
    print(all_area_codes)
```

### Create Search

```python
def create_search():
    from azure.communication.administration import CreateSearchOptions
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")
    area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_SEARCH', "area-code")

    searchOptions = CreateSearchOptions(
        area_code=area_code_for_search,
        description="testsearch20200014",
        display_name="testsearch20200014",
        phone_plan_ids=[phone_plan_id],
        quantity=1
    )
    search_response = phone_number_administration_client.begin_create_search(
        body=searchOptions
    )
    print(search_response.status())
```

### Get search by id
```python
def get_search_by_id():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID', "search-id")

    phone_number_search_response = phone_number_administration_client.get_search_by_id(
        search_id=search_id
    )
    print(phone_number_search_response)
```

### Purchase Search

```python
def purchase_search():
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_PURCHASE', "search-id")

    phone_number_administration_client.begin_purchase_search(
        search_id=search_id_to_purchase
    )
```

# Troubleshooting
The Azure Communication Service Identity client will raise exceptions defined in [Azure Core][azure_core].

# Next steps
## More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/communication/azure-communication-administration/samples) directory for detailed examples of how to use this library to manage identities and tokens.

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
[identitysamples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication/azure-communication-administration/samples/identity_samples.py
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
