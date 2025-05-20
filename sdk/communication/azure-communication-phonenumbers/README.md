# Azure Communication Phone Numbers Package client library for Python

Azure Communication Phone Numbers client package is used to administer Phone Numbers.

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started
## Prerequisites
- Python 3.7 or later is required to use this package.
- You must have an [Azure subscription](https://azure.microsoft.com/free/)
- A deployed Communication Services resource. You can use the [Azure Portal](https://learn.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://learn.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
## Install the package
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

#### Browsing and reserving phone numbers

The Browse and Reservations APIs provide an alternate way to acquire phone numbers via a shopping-cart-like experience. This is achieved by splitting the search operation, which finds and reserves numbers using a single LRO, into two separate synchronous steps, Browse and Reservation. 

The browse operation retrieves a random sample of phone numbers that are available for purchase for a given country, with optional filtering criteria to narrow down results. The returned phone numbers are not reserved for any customer.

Reservations represent a collection of phone numbers that are locked by a specific customer and are awaiting purchase. They have an expiration time of 15 minutes after the last modification or 2 hours from creation time. A reservation can include numbers from different countries, in contrast with the Search operation. Customers can Create, Retrieve, Modify (by adding and removing numbers), Delete, and Purchase reservations. Purchasing a reservation is an LRO.

### SIP routing client

Direct routing feature allows connecting customer-provided telephony infrastructure to Azure Communication Resources. In order to setup routing configuration properly, customer needs to supply the SIP trunk configuration and SIP routing rules for calls. SIP routing client provides the necessary interface for setting this configuration.

When a call is made, system tries to match the destination number with regex number patterns of defined routes. The first route to match the number will be selected. The order of regex matching is the same as the order of routes in configuration, therefore the order of routes matters.
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

#### Broswing and Reserving Available Phone Numbers

Use the Browse and Reservations API to reserve a phone number

```python
import uuid

browse_result = await phone_numbers_client.browse_available_phone_numbers(
    country_code="US",
    phone_number_type="tollFree"
)
number_to_reserve = browse_result.phone_numbers[0]

# The reservation ID needs to be a valid UUID.
reservation_id = str(uuid.uuid4())
reservation = await phone_numbers_client.create_or_update_reservation(
    reservation_id=reservation_id,
    numbers_to_add=[number_to_reserve]
)

numbers_with_error = [n for n in reservation.phone_numbers.values() if n.status == "error"]
if any(numbers_with_error):
    print("Errors occurred during reservation")
else:
    print("Reservation operation completed without errors.")
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
poller = phone_numbers_client.begin_release_phone_number(
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
poller = phone_numbers_client.begin_update_phone_number_capabilities(
    "<phone number>",
    PhoneNumberCapabilityType.OUTBOUND,
    PhoneNumberCapabilityType.INBOUND_OUTBOUND,
    polling = True
)
```

#### Purchase Reservation

Given an existing and active reservation, purchase the phone numbers in that reservation.

```python
reservation_id = "<reservation id>"
poller = phone_numbers_client.begin_purchase_reservation(
    reservation_id,
    polling = True
)
```

After the LRO finishes processing, the status of each individual number can be validated by retrieving the reservation.

```python
reservation_id = "<reservation id>"
reservation = phone_numbers_client.get_reservation(reservation_id)

numbers_with_error = [
    n for n in reservation.phone_numbers.values() if n.status == "error"]
if any(numbers_with_error):
    print("Errors occurred during purchase")
else:
    print("Reservation purchase completed without errors.")
```

### SipRoutingClient

#### Retrieve SIP trunks and routes

Get the list of currently configured trunks or routes.

```python
trunks = sip_routing_client.list_trunks()
for trunk in trunks:
    print(trunk.fqdn)
    print(trunk.sip_signaling_port)
routes = sip_routing_client.list_routes()
for route in routes:
    print(route.name)
    print(route.description)
    print(route.number_pattern)
    for trunk_fqdn in route.trunks:
        print(trunk_fqdn)
```

#### Replace SIP trunks and routes

Replace the list of currently configured trunks or routes with new values.

```python
new_trunks = [SipTrunk(fqdn="sbs1.contoso.com", sip_signaling_port=1122), SipTrunk(fqdn="sbs2.contoso.com", sip_signaling_port=1123)]
new_routes = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\+123[0-9]+", trunks=["sbs1.sipconfigtest.com"])]
sip_routing_client.set_trunks(new_trunks)
sip_routing_client.set_routes(new_routes)
```

#### Retrieve single trunk

```python
trunk = sip_routing_client.get_trunk("sbs1.contoso.com")
```

#### Set single trunk

```python
# Set function will either modify existing item or add new item to the collection.
# The trunk is matched based on it's FQDN.
new_trunk = SipTrunk(fqdn="sbs3.contoso.com", sip_signaling_port=5555)
sip_routing_client.set_trunk(new_trunk)
```

#### Delete single trunk

```python
sip_routing_client.delete_trunk("sbs1.contoso.com")
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
