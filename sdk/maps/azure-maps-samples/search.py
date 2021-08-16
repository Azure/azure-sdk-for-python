# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import json

from azure.maps.search.models import TextFormat
from azure.maps.search import SearchClient


parser = argparse.ArgumentParser(
    description='Search Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()


client = SearchClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

result = client.search.get_search_address(
    TextFormat.JSON, "15127 NE 24th Street, Redmond, WA 98052")
print("Get Search Address:")
print(result)


result = client.search.get_search_address_reverse(
    TextFormat.JSON, "37.337,-121.89")
print("Get Search Address Reverse:")
print(result)


result = client.search.get_search_address_reverse_cross_street(
    TextFormat.JSON, "37.337,-121.89")
print("Get Search Address Reverse Cross Street:")
print(result)


result = client.search.get_search_address_structured(
    TextFormat.JSON, None, "US", None, None, 15127, "NE 24th Street", None, "Redmond", None, None, None, "WA", "98052")
print("Get Search Address Structured:")
print(result)


results = client.search.get_search_fuzzy(TextFormat.JSON, "seattle")
print("Get Search Fuzzy:")
print(results)
ids = list(map(lambda result: result.data_sources.geometry.id, results.results))


result = client.search.get_search_nearby(
    TextFormat.JSON, 40.706270, -74.011454, 10, None, None, None, 8046)
print("Get Search Fuzzy:")
print(result)


result = client.search.get_search_poi(
    TextFormat.JSON, "juice bars", None, 5, None, None, None, 47.606038, -122.333345, 8046)
print("Get Search POI:")
print(result)


result = client.search.get_search_poi_category(
    TextFormat.JSON, "atm", None, 5, None, None, None, 47.606038, -122.333345, 8046)
print("Get Search POI Category:")
print(result)


result = client.search.get_search_poi_category_tree_preview(TextFormat.JSON)
print("Get Search POI Category Tree:")
print(result)


result = client.search.get_search_polygon(TextFormat.JSON, ids)
print("Get Search Polygon:")
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
