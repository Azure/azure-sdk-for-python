# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_copy_blob.py
DESCRIPTION:
    This sample demos how to copy a blob from a URL.
USAGE: python blob_samples_copy_blob.py
    Set the environment variables with your own values before running the sample.
    1) STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import sys
import time
from azure.storage.blob import BlobServiceClient

def main():
    try:
        CONNECTION_STRING = os.environ['STORAGE_CONNECTION_STRING']

    except KeyError:
        print("STORAGE_CONNECTION_STRING must be set.")
        sys.exit(1)

    status = None
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
    blob_service_client.create_container('mycontainer')
    copied_blob = blob_service_client.get_blob_client("mycontainer", '59466-0.txt')
    # Copy started
    copied_blob.start_copy_from_url(source_blob)
    for i in range(10):
        props = copied_blob.get_blob_properties()
        if props.copy.status is not None:
            status = props.copy.status
        else:
            status = "None"
        print("Copy status: " + status)
        if status == "success":
            # Copy finished
            break
        time.sleep(10)

    if status != "success":
        # if not finished after 100s, cancel the operation
        props = copied_blob.get_blob_properties()
        print(props.copy.status)
        copy_id = props.copy.id
        if copy_id is not None:
            copied_blob.abort_copy(copy_id)
        else:
            print("copy_id was unexpectedly None, check if the operation completed successfully.")
            sys.exit(1)
        props = copied_blob.get_blob_properties()
        print(props.copy.status)

if __name__ == "__main__":
    main()
