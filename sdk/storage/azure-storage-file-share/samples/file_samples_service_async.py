# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_service_async.py

DESCRIPTION:
    These samples demonstrate file share service operations like setting and getting
    service properties, listing the shares within the service, and getting a share
    client.

USAGE:
    python file_samples_service_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import asyncio
import os

SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class FileShareServiceSamplesAsync(object):

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    async def file_service_properties_async(self):
        # Instantiate the ShareServiceClient from a connection string
        from azure.storage.fileshare.aio import ShareServiceClient
        file_service = ShareServiceClient.from_connection_string(self.connection_string)

        # [START set_service_properties]
        # Create service properties
        from azure.storage.fileshare import Metrics, CorsRule, RetentionPolicy

        # Create metrics for requests statistics
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create CORS rules
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])
        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        async with file_service:
            # Set the service properties
            await file_service.set_service_properties(hour_metrics, minute_metrics, cors)
        # [END set_service_properties]

            # [START get_service_properties]
            properties = await file_service.get_service_properties()
            # [END get_service_properties]

    async def list_shares_in_service_async(self):
        # Instantiate the ShareServiceClient from a connection string
        from azure.storage.fileshare.aio import ShareServiceClient
        file_service = ShareServiceClient.from_connection_string(self.connection_string)

        async with file_service:
            # [START fsc_create_shares]
            await file_service.create_share(share_name="fileshare1")
            # [END fsc_create_shares]
            try:
                # [START fsc_list_shares]
                # List the shares in the file service
                my_shares = []
                async for s in file_service.list_shares():
                    my_shares.append(s)

                # Print the shares
                for share in my_shares:
                    print(share)
                # [END fsc_list_shares]

            finally:
                # [START fsc_delete_shares]
                await file_service.delete_share(share_name="fileshare1")
                # [END fsc_delete_shares]

    async def get_share_client_async(self):
        # [START get_share_client]
        from azure.storage.fileshare.aio import ShareServiceClient
        file_service = ShareServiceClient.from_connection_string(self.connection_string)

        # Get a share client to interact with a specific share
        share = file_service.get_share_client("fileshare2")
        # [END get_share_client]


async def main():
    sample = FileShareServiceSamplesAsync()
    await sample.file_service_properties_async()
    await sample.list_shares_in_service_async()
    await sample.get_share_client_async()

if __name__ == '__main__':
    asyncio.run(main())
