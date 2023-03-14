# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: example_shared_transport.py

DESCRIPTION:
    This sample demonstrates how to share transport connections between multiple clients.

USAGE:
    python example_shared_transport.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the endpoint of your Azure Metrics Advisor service
"""

import os
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobServiceClient

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


def shared_transport():
    # [START shared_transport]
    shared_transport = RequestsTransport()
    with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False  # here we set session_owner to False to indicate that we don't want to close the session when the client is closed
        )
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string, transport=shared_transport, session_owner=False
        )
        containers1 = blob_service_client1.list_containers()
        for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        for contain in containers2:
            print(contain.name)
    # [END shared_transport]


def shared_transport_with_pooling():
    # [START shared_transport_with_pooling]
    import requests

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    shared_transport = RequestsTransport(session=session)
    with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string, transport=shared_transport, session_owner=False
        )
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string, transport=shared_transport, session_owner=False
        )
        containers1 = blob_service_client1.list_containers()
        for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        for contain in containers2:
            print(contain.name)
    # [END shared_transport_with_pooling]


if __name__ == "__main__":
    shared_transport()
    shared_transport_with_pooling()
