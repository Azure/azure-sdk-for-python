# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy

from azure.maps.elevation.models import ResponseFormat, CoordinatesPairAbbreviated
from azure.maps.elevation import ElevationClient


parser = argparse.ArgumentParser(
    description='Elevation Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = ElevationClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

result = client.elevation.get_data_for_bounding_box(ResponseFormat.JSON, [
    "-121.66853362143818", "46.84646479863713", "-121.65853362143818", "46.85646479863713"], rows=3, columns=3)
print("Get Data for bounding box")
print(result)
print("Data array:")
for point_result in result.data:
    print(point_result)


result = client.elevation.get_data_for_points(ResponseFormat.JSON, [
    "-121.66853362143818,46.84646479863713", "-121.65853362143818,46.85646479863713"])
print("Get Data for points")
print(result)
print("Data array:")
for point_result in result.data:
    print(point_result)


result = client.elevation.get_data_for_polyline(ResponseFormat.JSON, [
    "-121.66853362143818,46.84646479863713", "-121.65853362143818,46.85646479863713"])
print("Get Data for polyline")
print(result)
print("Data array:")
for point_result in result.data:
    print(point_result)


coord1 = CoordinatesPairAbbreviated(
    lat=46.84646479863713, lon=-121.66853362143818)
coord2 = CoordinatesPairAbbreviated(
    lat=46.856464798637127, lon=-121.68853362143818)
result = client.elevation.post_data_for_points(
    ResponseFormat.JSON, [coord1, coord2])
print("Get Data for multiple points")
print(result)
print("Data array:")
for point_result in result.data:
    print(point_result)


result = client.elevation.post_data_for_polyline(
    ResponseFormat.JSON, [coord1, coord2])
print("Get Data for long polyline")
print(result)
print("Data array:")
for point_result in result.data:
    print(point_result)
