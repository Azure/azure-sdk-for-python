# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
from common.common import AzureKeyInQueryCredentialPolicy
import os
from azure.core.credentials import AzureKeyCredential

from azure.maps.geolocation.models import ResponseFormat
from azure.maps.geolocation import GeolocationClient
    


client = GeolocationClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

parser = argparse.ArgumentParser(
    description='Geolocation Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--ip', action="store", required=True)
ip = parser.parse_args().ip

result = client.geolocation.get_ip_to_location_preview(ResponseFormat.JSON, ip)
print("Got location by ip")
print(result)
print(result.country_region)
