# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
try:
    import settings_real as settings
except ImportError:
    import file_settings_fake as settings

from filetestcase import (
    FileTestCase,
    TestMode,
    record
)


class TestFileServiceSamples(FileTestCase):

    connection_string = settings.CONNECTION_STRING

    async def _test_file_service_properties(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # [START set_service_properties]
        # Create service properties
        from azure.storage.file.aio import Metrics, CorsRule, RetentionPolicy

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

        # Set the service properties
        await file_service.set_service_properties(hour_metrics, minute_metrics, cors)
        # [END set_service_properties]

        # [START get_service_properties]
        properties = await file_service.get_service_properties()
        # [END get_service_properties]

    def test_file_service_properties(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_file_service_properties())

    async def _test_share_operations(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # [START fsc_create_shares]
        await file_service.create_share(share_name="testshare")
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
            await file_service.delete_share(share_name="testshare")
            # [END fsc_delete_shares]

    def test_share_operations(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_share_operations())

    async def _test_get_share_client(self):
        # [START get_share_client]
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Get a share client to interact with a specific share
        share = await file_service.get_share_client("fileshare")
        # [END get_share_client]

    def test_get_share_client(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_share_client())
