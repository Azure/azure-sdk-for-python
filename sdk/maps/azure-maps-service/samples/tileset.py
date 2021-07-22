# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os
import re

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy

from azure.core.exceptions import HttpResponseError
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='Tileset Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--dataset_id', action="store", required=True)
dataset_id = parser.parse_args().dataset_id

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

(deserialized, headers) = client.tileset.begin_create(dataset_id, "Test Description",
                                                      cls=lambda _, deserialized, headers: (deserialized, headers)).result()

tileset_id = re.search(
    "[0-9A-Fa-f\-]{36}", headers["Resource-Location"]).group()

if deserialized.status != "Succeeded":
    print("Tileset creation faled")
    exit(0)
try:
    result = client.tileset.get(tileset_id)
    print("Get tileset with tilesetId {}".format(tileset_id))
    print(result)

    result = client.tileset.list()
    print("View all tilesets:")
    for tileset_info in result:
        print(tileset_info)
except HttpResponseError as e:
    print(e)
finally:
    client.tileset.delete(tileset_id)
    print("Deleted tileset with tilesetId {}".format(tileset_id))
