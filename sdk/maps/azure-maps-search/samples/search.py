# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy

from azure.maps.search import *
from azure.maps.search.models import LatLon, StructuredAddress

"""
In this samples, I have used AzureCredential and Azure_Subscription_Key as the way to authenticate the SearchClient.

There is another way of authentication, to use an Azure Active Directory (AAD) token credential,
provide an instance of the desired credential type obtained from the azure-identity library.

Authentication with AAD requires some initial setup:
- Install azure-identity
- Register a new AAD application

After setup, you can choose which type of credential from azure.identity to use.
As an example, `DefaultAzureCredential()` can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:

set `AZURE_CLIENT_ID` = <RealClientId>
set `AZURE_TENANT_ID` = <RealTenantId>
set `AZURE_CLIENT_SECRET` = <RealClientSecret>

from azure.maps.search import SearchClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
search_client = SearchClient(credential=credential)
"""

parser = argparse.ArgumentParser(
    description='Search Samples Program. Set AZURE_SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = SearchClient(
    credential=AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY")),
)


results = client.fuzzy_search("seattle", coordinates=LatLon(47.60323, -122.33028))
print("Get Search Fuzzy with coordinates:")
print(results)


result = client.reverse_search_address(coordinates=LatLon(25.0338053, 121.5640089))
print("Get Search Address Reverse:")
print(result)


result = client.reverse_search_cross_street_address(coordinates=LatLon(25.0338053, 121.5640089))
print("Get Search Address Reverse Cross Street:")
print(result)

# cSpell:disable
addr = StructuredAddress(street_number="221",
                                 street_name="Sec. 2, Zhishan Rd.",
                                 municipality_subdivision="Shilin Dist.",
                                 municipality="Taipei City",
                                 country_code="TW")
result = client.search_structured_address(addr)
print("Get Search Address Structured:")
print(result)


result = client.search_nearby_point_of_interest(coordinates=LatLon(25.0338053, 121.5640089))
print("Get Search Nearby point of interest:")
print(result)


result = client.search_point_of_interest("juice bars")
print("Get Search POI:")
print(result)


result = client.search_point_of_interest_category("RESTAURANT", coordinates=LatLon(25.0338053, 121.5640089))
print("Get Search POI Category:")
print(result)


result = client.get_point_of_interest_categories()
print("Get Search POI Categories:")
print(result)
