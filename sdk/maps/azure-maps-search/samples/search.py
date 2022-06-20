# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import json

from azure.maps.search import *

parser = argparse.ArgumentParser(
    description='Search Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()


client = SearchClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))


results = client.search.fuzzy_search("seattle", {"lat": 2.2, "lon": 3.3})
print("Get Search Fuzzy with coordinates:")
print(results)
ids = list(map(lambda result: result.data_sources.geometry.id, results.results))


result = client.get_geometries(ids)
print("Get Search Address by Geomtry ids:")
print(result)


result = client.reverse_search_address({"lat": 37.337, "lon": -121.89})
print("Get Search Address Reverse:")
print(result)


result = client.reverse_search_cross_street_address({"lat": 37.337, "lon": -121.89})
print("Get Search Address Reverse Cross Street:")
print(result)


result = client.search_structured_address("US", 15127, "NE 24th Street", "Redmond", "WA", "98052")
print("Get Search Address Structured:")
print(result)


result = client.search_nearby_point_of_interest({"lat": 40.706270, "lon": -74.011454}, 10, 8046)
print("Get Search Fuzzy:")
print(result)


result = client.search_point_of_interest("juice bars", "US")
print("Get Search POI:")
print(result)


result = client.search_point_of_interest_category("atm", None, 5, None, None, None, 47.606038, -122.333345, 8046)
print("Get Search POI Category:")
print(result)


result = client.get_point_of_interest_category_tree()
print("Get Search POI Category Tree:")
print(result)


with open("resources/search_address_batch_request_body.json", "r") as file:
    poller = client.search.begin_post_search_address_batch(
        TextFormat.JSON, json.load(file))
    result = poller.result()
    print("Post Search Address Batch")
    print(result)


with open("resources/search_address_reverse_batch_request_body.json", "r") as file:
    poller = client.search.begin_post_search_address_reverse_batch(
        TextFormat.JSON, json.load(file))
    result = poller.result()
    print("Post Search Address Reverse Batch")
    print(result)


with open("resources/search_fuzzy_batch_request_body.json", "r") as file:
    poller = client.search.begin_post_search_fuzzy_batch(
        TextFormat.JSON, json.load(file))
    result = poller.result()
    print("Post Search Fuzzy Batch")
    print(result)


with open("resources/search_along_route_request_body.json", "r") as file:
    result = client.search.post_search_along_route(
        TextFormat.JSON, "burger", 1000, json.load(file), limit=2)
    print("Post Search Along Route")
    print(result)


with open("resources/search_inside_geometry_request_body.json", "r") as file:
    result = client.search.post_search_inside_geometry(
        TextFormat.JSON, "burger", json.load(file), limit=2)
    print("Post Search Inside Geometry")
    print(result)