# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import os
from common.common import AzureKeyInQueryCredentialPolicy
import json
import argparse

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='Featurestate Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--dataset_id', action="store", required=True)
dataset_id = parser.parse_args().dataset_id

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

with open("resources/featurestate_sample_create.json", "r") as file:
    style = json.load(file)
    result = client.feature_state.create_stateset(dataset_id, style)
    print("Created stateset")
    print(result)
    stateset_id = result.stateset_id
feature_id = "SPC4709"
state_key_names = "keyName1"
try:
    result = client.feature_state.list_stateset()
    print("List statesets:")
    for stateset in result:
        print(stateset)

    stateset = client.feature_state.get_stateset(stateset_id)
    print("Get states with stateset_id {}".format(stateset_id))
    print(stateset)

    feature_state_structure = client.feature_state.get_states(
        stateset_id, feature_id)
    print("Get states with stateset_id {} and feature_id {}".format(
        stateset_id, feature_id))
    print(feature_state_structure)

    with open("resources/featurestate_sample_put", "r") as file:
        style = json.load(file)
        result = client.feature_state.put_stateset(stateset_id, style)
        print("Updated stateset")
        print(result)

    with open("resources/featurestate_sample_update_states.json", "r") as file:
        states = json.load(file)
        result = client.feature_state.update_states(stateset_id, states)
        print("Updated stateset")
        print(result)

    client.feature_state.delete_state(stateset_id, feature_id, state_key_name)
    print("Deleted state")
except HttpResponseError as e:
    print(e)
finally:
    client.feature_state.delete_stateset(stateset_id)
    print("Deleted stateset")
