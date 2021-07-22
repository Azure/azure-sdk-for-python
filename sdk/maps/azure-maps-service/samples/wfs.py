# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='WFS Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--dataset_id', action="store", required=True)
dataset_id = parser.parse_args().dataset_id

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

client.wfs.delete_feature(dataset_id, "facility", "FCL39")
print("Delete Feature")


result = client.wfs.get_collection(dataset_id, "facility")
print("Get Collection")
print(result)


result = client.wfs.get_collection_definition(dataset_id, "facility")
print("Get Collection Definition")
print(result)


result = client.wfs.get_collections(dataset_id)
print("Get Collections")
print(result)


result = client.wfs.get_conformance(dataset_id)
print("Get Conformance")
print(result)


result = client.wfs.get_feature(dataset_id, "unit", "UNIT39")
print("Get Feature")
print(result)


result = client.wfs.get_features(dataset_id, "unit", 1, "-123,46,-120,47")
print("Get Features")
print(result)


result = client.wfs.get_landing_page(dataset_id)
print("Get Landing Page")
print(result)
