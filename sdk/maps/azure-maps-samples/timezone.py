# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy

from azure.maps.timezone.models import ResponseFormat, TimezoneOptions
from azure.maps.timezone import TimezoneClient

parser = argparse.ArgumentParser(
    description='Timezone Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()


client = TimezoneClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

result = client.timezone.get_timezone_by_coordinates(
    ResponseFormat.JSON, "47.0,-122", None, TimezoneOptions.ALL)
print("Get Timezone By Coordinate")
print(result)


result = client.timezone.get_timezone_by_id(
    ResponseFormat.JSON, "Asia/Bahrain", None, TimezoneOptions.ALL)
print("Get Timezone By Id")
print(result)


result = client.timezone.get_timezone_enum_iana(ResponseFormat.JSON)
print("Get Timezone Enum IANA")
print(result)


result = client.timezone.get_timezone_enum_windows(ResponseFormat.JSON)
print("Get Timezone Enum Windows")
print(result)


result = client.timezone.get_timezone_iana_version(ResponseFormat.JSON)
print("Get Timezone IANA Version")
print(result)


result = client.timezone.get_timezone_windows_to_iana(
    ResponseFormat.JSON, "pacific standard time")
print("Get Timezone Windows to IANA")
print(result)