# Azure Communication Phone Numbers Package client library for Python

Azure Communication Phone Numbers client package is used to administer Phone Numbers.

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started
### Prerequisites
- Python 3.6 or later is required to use this package.
- You must have an [Azure subscription](https://azure.microsoft.com/free/)
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
### Install the package
Install the Azure Communication Phone Numbers client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-phonenumbers
```

## Key concepts

This SDK provides functionality to easily manage `direct offer` and `direct routing` numbers.

The `direct offer` numbers come in two types: Geographic and Toll-Free. Geographic phone plans are phone plans associated with a location, whose phone numbers' area codes are associated with the area code of a geographic location. Toll-Free phone plans are phone plans not associated location. For example, in the US, toll-free numbers can come with area codes such as 800 or 888.
They are managed using the `PhoneNumbersClient`

The `direct routing` feature enables connecting your existing telephony infrastructure to ACS.
The configuration is managed using the `SipRoutingClient`, which provides methods for setting up SIP trunks and voice routing rules, in order to properly handle calls for your telephony subnet.

### Initializing Client
Client can be initialized using the AAD authentication.

```python
import os
from azure.communication.phonenumbers import PhoneNumbersClient
from azure.identity import DefaultAzureCredential

endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have your
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
phone_numbers_client = PhoneNumbersClient(endpoint, DefaultAzureCredential())
```

```python
import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient
from azure.identity import DefaultAzureCredential

endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have your
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
sip_routing_client = SipRoutingClient(endpoint, DefaultAzureCredential())
```

Another option is to initialize the client using connection string of the resource.

```python
# You can find your connection string from your resource in the Azure Portal
import os
from azure.communication.phonenumbers import PhoneNumbersClient

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)
```

```python
# You can find your connection string from your resource in the Azure Portal
import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
sip_routing_client = SipRoutingClient.from_connection_string(connection_str)
```

### Phone numbers client

#### Phone number types overview

Phone numbers come in two types; Geographic and Toll-Free. Geographic phone numbers are phone numbers associated with a location, whose area codes are associated with the area code of a geographic location. Toll-Free phone numbers are phone numbers with no associated location. For example, in the US, toll-free numbers can come with area codes such as 800 or 888.

#### Searching and Purchasing and Releasing numbers

Phone numbers can be searched through the search creation API by providing an area code, quantity of phone numbers, application type, phone number type, and capabilities. The provided quantity of phone numbers will be reserved for ten minutes and can be purchased within this time. If the search is not purchased, the phone numbers will become available to others after ten minutes. If the search is purchased, then the phone numbers are acquired for the Azure resources.

Phone numbers can also be released using the release API.

### SIP routing client

Direct routing feature allows connecting customer-provided telephony infrastructure to Azure Communication Resources. In order to setup routing configuration properly, customer needs to supply the SIP trunk configuration and SIP routing rules for calls. SIP routing client provides the necessary interface for setting this configuration.

When the call arrives, system tries to match the destination number with regex number patterns of defined routes. The first route to match the number will be selected. The order of regex matching is the same as the order of routes in configuration, therefore the order of routes matters.
Once a route is matched, the call is routed to the first trunk in the route's trunks list. If the trunk is not available, next trunk in the list is selected.

## Examples

### PhoneNumbersClient

#### Get All Purchased Phone Numbers

Lists all of your purchased phone numbers

```python
purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
for acquired_phone_number in purchased_phone_numbers:
    print(acquired_phone_number.phone_number)
```

#### Get Purchased Phone Number

Gets the information from the specified phone number

```python
result = phone_numbers_client.get_purchased_phone_number("<phone number>")
print(result.country_code)
print(result.phone_number)
```

### Long Running Operations

The Phone Number Client supports a variety of long running operations that allow indefinite polling time to the functions listed down below.

#### Search for Available Phone Number

You can search for available phone numbers by providing the capabilities of the phone you want to acquire, the phone number type, the assignment type, and the country code. It's worth mentioning that for the toll-free phone number type, proving the area code is optional.
The result of the search can then be used to purchase the number in the corresponding API.

```python
capabilities = PhoneNumberCapabilities(
        calling = PhoneNumberCapabilityType.INBOUND,
        sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
    )
poller = phone_numbers_client.begin_search_available_phone_numbers(
    "US",
    PhoneNumberType.TOLL_FREE,
    PhoneNumberAssignmentType.APPLICATION,
    capabilities,
    area_code ="833", # Area code is optional for toll-free numbers
    quantity = 2, # Quantity is optional. If not set, default is 1
    polling = True
)
search_result = poller.result()
```

#### Purchase Phone Numbers

The result of your search can be used to purchase the specified phone numbers. This can be done by passing the `search_id` from the search response to the purchase phone number API.

```python
purchase_poller = phone_numbers_client.begin_purchase_phone_numbers(
    search_result.search_id,
    polling=True
)
```

#### Release Phone Number

Releases an acquired phone number.

```python
poller = self.phone_number_client.begin_release_phone_number(
    "<phone number>",
    polling = True
)
```

#### Updating Phone Number Capabilities

Updates the specified phone number capabilities for Calling and SMS to one of:

- `PhoneNumberCapabilityType.NONE`
- `PhoneNumberCapabilityType.INBOUND`
- `PhoneNumberCapabilityType.OUTBOUND`
- `PhoneNumberCapabilityType.INBOUND_OUTBOUND`

```python
poller = self.phone_number_client.begin_update_phone_number_capabilities(
    "<phone number>",
    PhoneNumberCapabilityType.OUTBOUND,
    PhoneNumberCapabilityType.INBOUND_OUTBOUND,
    polling = True
)
```

### SipRoutingClient

#### Retrieve SIP trunks and routes

Get the list of currently configured trunks or routes.

```python
trunks = sip_routing_client.get_trunks()
routes = sip_routing_client.get_routes()
```

#### Replace SIP trunks and routes

Replace the list of currently configured trunks or routes with new values.

```python
sip_routing_client.set_trunks("<list of new trunks>")
sip_routing_client.set_routes("<list of new routes>")
```

#### Retrieve single trunk

```python
trunk = sip_routing_client.get_trunk("<trunk FQDN>")
```

#### Set single trunk

```python
# Set function will either modify existing item or add new item to the collection.
# The trunk is matched based on it's FQDN.
sip_routing_client.set_trunk("<new trunk>")
```

#### Delete single trunk

```python
sip_routing_client.delete_trunk("<trunk FQDN>")
```

# Troubleshooting
The Phone Numbers Administration client will raise exceptions defined in [Azure Core][azure_core].

# Next steps
## More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-phonenumbers/samples) directory for detailed examples of how to use this library.

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
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
