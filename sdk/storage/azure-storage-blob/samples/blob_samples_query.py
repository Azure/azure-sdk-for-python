# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_query.py
DESCRIPTION:
    This sample demos how to read quick query data.
USAGE: python blob_samples_query.py
    Set the environment variables with your own values before running the sample.
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""
import os
import sys
from azure.storage.blob import BlobServiceClient


def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    except KeyError:
        print("AZURE_STORAGE_CONNECTION_STRING must be set.")
        sys.exit(1)

    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_name = "quickquerycontainer"
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()
    # [START query]
    errors = []

    def progress_callback(error, bytes_processed, total_bytes):
        if error:
            errors.append(error)
        if not bytes_processed:
            print("All bytes have been processed")
            print("Total Bytes processed should be {}".format(total_bytes))
        else:
            print(bytes_processed)

    # upload the csv file
    blob_client = blob_service_client.get_blob_client(container_name, "csvfile")
    with open("./sample-blobs/query.csv", "rb") as stream:
        blob_client.upload_blob(stream)

    # select the second column of the csv file
    query_expression = "SELECT _2 from BlobStorage"
    reader = blob_client.query(query_expression, progress_callback=progress_callback)
    content = reader.readall()
    # [END query]
    print(content)

    container_client.delete_container()


if __name__ == "__main__":
    main()
