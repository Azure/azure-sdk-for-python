# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from common.common import AzureKeyInQueryCredentialPolicy
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='Alias Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--creator_data_item_id', action="store")
creator_data_item_id = parser.parse_args().creator_data_item_id

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

print("Create alias:")
alias_create_response = client.alias.create()
print(alias_create_response)

alias_id = alias_create_response.alias_id
try:
    print("Assign resource:")
    alias_list_item = client.alias.assign(alias_id, creator_data_item_id)
    print(alias_list_item)

    print("Get details:")
    alias_list_item = client.alias.get_details(alias_id)
    print(alias_list_item)

    print("List aliases:")
    aliases = client.alias.list()
    for alias_list_item in aliases:
        print(alias_list_item)
except HttpResponseError as e:
    print(e)
finally:
    print("Delete alias:")
    client.alias.delete(alias_id)
