# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os
import re

from azure.core.credentials import AzureKeyCredential, HttpResponseError
from common.common import AzureKeyInQueryCredentialPolicy
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='Dataset Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--conversion_id', action="store", required=True)
parser.add_argument('--dont_delete',
                    action="store_true", default=False)
conversion_id = parser.parse_args().conversion_id

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))
(deserialized, headers) = client.dataset.begin_create(conversion_id, cls=lambda _, deserialized, headers: (deserialized, headers)).result()
dataset_id = re.search("[0-9A-Fa-f\-]{36}", headers["Resource-Location"]).group()
print("Created dataset with id {}".format(dataset_id))
try:
    datasets = client.dataset.list()
    print("View all previously created datasets:")
    for dataset_list_item in datasets:
        print(dataset_list_item)

    result = client.dataset.get(dataset_id)
    print("Get dataset with id {}".format(dataset_id))
    print(result)
except HttpResponseError as e:
    print(e)
finally:
    client.dataset.delete(dataset_id)
    print("Deleted dataset with id {}".format(dataset_id))
