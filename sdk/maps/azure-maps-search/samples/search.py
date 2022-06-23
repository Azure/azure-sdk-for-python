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

parser = argparse.ArgumentParser(
    description='Search Samples Program. Set AZURE_SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = SearchClient(
    credential='None',
    client_id=os.environ.get("AZURE_CLIENT_ID"),
    authentication_policy=AzureKeyInQueryCredentialPolicy(
        AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY")),
        'subscription-key'
    )
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
