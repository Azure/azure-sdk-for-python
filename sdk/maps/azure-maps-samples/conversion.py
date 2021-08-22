# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os
import re

from azure.core.exceptions import HttpResponseError

from azure.core.credentials import AzureKeyCredential
from azure.maps.creator import CreatorClient
from common.common import AzureKeyInQueryCredentialPolicy

parser = argparse.ArgumentParser(
    description='Conversion Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--udid', action="store", required=True)
udid = parser.parse_args().udid

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))


(deserialized, headers) = client.conversion.begin_convert(
    udid, "facility-2.0", cls=lambda _, deserialized, headers: (deserialized, headers)).result()

conversion_id = re.search(
    "[0-9A-Fa-f\-]{36}", headers["Resource-Location"]).group()

if deserialized.status != "Succeeded":
    print("Conversion failed")
    exit(0)
try:
    conversionInfo = client.conversion.get(conversion_id)
    print(conversionInfo)

    conversions = client.conversion.list()
    print("Viewing all conversions:")
    for conversionInfo in conversions:
        print(conversionInfo)
except HttpResponseError as e:
    print(e)
finally:
    client.conversion.delete(conversion_id)
    print("Deleted conversion with conversion_id {}".format(conversion_id))
