# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse
import os
import re

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import json

from azure.core.exceptions import HttpResponseError

from azure.maps.creator.models import UploadDataFormat
from azure.maps.creator import CreatorClient

parser = argparse.ArgumentParser(
    description='Data Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = CreatorClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

print("Uploading zip file")
with open("resources/data_sample_upload.zip", "rb") as file:
    (deserialized, headers) = client.data.begin_upload_preview(UploadDataFormat.DWGZIPPACKAGE,
                                                               file.read(), "Upload Description", content_type="application/octet-stream",
                                                               cls=lambda _, deserialized, headers: (deserialized, headers)).result()
    if deserialized.status != "Succeeded":
        print("Zip file upload faled")
        exit(0)
    udid = re.search("[0-9A-Fa-f\-]{36}", headers["Resource-Location"]).group()

    client.data.delete_preview(udid)

print("Uploading json file")
with open("resources/data_sample_upload.json", "r") as file:
    (deserialized, headers) = client.data.begin_upload_preview(UploadDataFormat.GEOJSON,
                                                               json.load(file), "Upload Description", content_type="application/json",
                                                               cls=lambda _, deserialized, headers: (deserialized, headers)).result()
    if deserialized.status != "Succeeded":
        print("File upload failed")
        exit(0)
    udid = re.search("[0-9A-Fa-f\-]{36}", headers["Resource-Location"]).group()
    try:
        print("View all uploaded files:")
        for map_data_detail in client.data.list_preview().map_data_list:
            print(map_data_detail)

        fileData = client.data.download_preview(udid)
        bytes = bytearray()
        for line in fileData:
            bytes.extend(line)
        print("Downloaded file with udid {}".format(udid))
        print(bytes)

        with open("resources/data_sample_update.json", "r") as file:
            print("Update file with udid {}".format(udid))
            result = client.data.begin_update_preview(udid, json.load(file),
                                                      "Update Description").result()
            print(result.status)
    except HttpResponseError as e:
        print(e)
    finally:
        client.data.delete_preview(udid)
        print("Deleted file with udid {}".format(udid))
