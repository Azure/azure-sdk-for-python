# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    record
)


class TestFileServiceSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    def test_file_service_properties(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Create service properties
        from azure.storage.file import Metrics, CorsRule, RetentionPolicy

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
        file_service.set_service_properties(hour_metrics, minute_metrics, cors)

        # Get queue service properties
        properties = file_service.get_service_properties()

    @record
    def test_share_operations(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Create a file share
        file_service.create_share(share_name="testshare")

        try:
            # List the shares in the file service
            my_shares = list(file_service.list_shares())

            # Print the shares
            for share in my_shares:
                print(share)

        finally:
            # Delete the file share
            file_service.delete_share(share_name="testshare")

    @record
    def test_get_share_client(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Get a share client to interact with a specific share
        share = file_service.get_share_client("fileshare")
