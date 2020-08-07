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
from azure.storage.blob import BlobServiceClient, DelimitedJsonDialect, DelimitedTextDialect


def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    except KeyError:
        print("AZURE_STORAGE_CONNECTION_STRING must be set.")
        sys.exit(1)

    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_name = "quickquerycontainer"
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except:
        pass
    # [START query]
    errors = []
    def on_error(error):
        errors.append(error)

    # upload the csv file
    blob_client = blob_service_client.get_blob_client(container_name, "csvfile")
    with open("./sample-blobs/quick_query.csv", "rb") as stream:
        blob_client.upload_blob(stream, overwrite=True)

    # select the second column of the csv file
    query_expression = "SELECT _2 from BlobStorage"
    input_format = DelimitedTextDialect(delimiter=',', quotechar='"', lineterminator='\n', escapechar="", has_header=False)
    output_format = DelimitedJsonDialect(delimiter='\n')
    reader = blob_client.query_blob(query_expression, on_error=on_error, blob_format=input_format, output_format=output_format)
    content = reader.readall()
    # [END query]
    print(content)

    container_client.delete_container()


if __name__ == "__main__":
    main()
