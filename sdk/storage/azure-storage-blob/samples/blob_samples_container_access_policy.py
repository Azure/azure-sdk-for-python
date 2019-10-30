# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_container_access_policy.py

DESCRIPTION:
    This example shows how to set the container access policy when creating the container
    and also how to get the access policy of a container after the container has been
    created. This sample expects that the `AZURE_STORAGE_CONNECTION_STRING` environment
    variable is set. It SHOULD NOT be hardcoded in any code derived from this sample.

USAGE: python blob_samples_container_access_policy.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account

EXAMPLE OUTPUT:

..Creating container
Created container has identifier 'read' with permissions 'rw', start date '2019-10-18T22:14:36Z', and expiry date '2019-10-18T23:15:36Z'.

..Getting container access policy
Blob Access Type: container
Identifier 'read' has permissions 'rw'
"""

import os
import sys
from datetime import datetime, timedelta

from azure.storage.blob import AccessPolicy, BlobServiceClient, ContainerSasPermissions, PublicAccess

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    sys.exit(1)

def get_and_set_container_access_policy():
    service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = service_client.get_container_client("mynewconwertainer")

    print("\n..Creating container")
    container_client.create_container()

    # Create access policy
    access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True, write=True),
                                    expiry=datetime.utcnow() + timedelta(hours=1),
                                    start=datetime.utcnow() - timedelta(minutes=1))

    identifiers = {'read': access_policy}

    # Specifies full public read access for container and blob data.
    public_access = PublicAccess.Container

    # Set the access policy on the container
    container_client.set_container_access_policy(signed_identifiers=identifiers, public_access=public_access)

    for identifier_name, access_policy in identifiers.items():
        print(
            "Created container has identifier '{}' with permissions '{}', start date '{}', and expiry date '{}'.".format(
                identifier_name, access_policy.permission, access_policy.start, access_policy.expiry
            )
        )

    # Get the access policy on the container
    print("\n..Getting container access policy")
    access_policy = container_client.get_container_access_policy()
    print(f"Blob Access Type: {access_policy['public_access']}")
    for identifier in access_policy['signed_identifiers']:
        print(f"Identifier '{identifier.id}' has permissions '{identifier.access_policy.permission}''")


try:
    get_and_set_container_access_policy()
except Exception as error:
    print(error)
    sys.exit(1)
