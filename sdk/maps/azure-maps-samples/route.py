# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import json

from azure.maps.route.models import TextFormat, RouteType
from azure.maps.route import RouteClient


parser = argparse.ArgumentParser(
    description='Route Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = RouteClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))


result = client.route.get_route_directions(
    TextFormat.JSON, "52.50931,13.42936:52.50274,13.43872")
print("Get route directions")
print(result)


result = client.route.get_route_range(
    TextFormat.JSON, "50.97452,5.86605", time_budget_in_sec=6000)
print("Get route range")
print(result)


with open("resources/route_directions_request_body.json") as file:
    result = client.route.post_route_directions(
        TextFormat.JSON, "52.50931,13.42936:52.50274,13.43872", json.load(file))
    print("Post route directions")
    print(result)
    for route in result.routes:
        print(route)


with open("resources/route_directions_batch_request_body.json") as file:
    poller = client.route.begin_post_route_directions_batch(
        TextFormat.JSON, json.load(file))
    print("Post route directions batch")
    print(poller.result())


with open("resources/route_matrix_request_body.json") as file:
    poller = client.route.begin_post_route_matrix(
        TextFormat.JSON, json.load(file), route_type=RouteType.SHORTEST, wait_for_results=True)
    print("Post route matrix")
    print(poller.result())
