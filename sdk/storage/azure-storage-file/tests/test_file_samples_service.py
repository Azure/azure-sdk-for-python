# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from filetestcase import (
    FileTestCase
)




class TestFileServiceSamples(FileTestCase):

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_file_service_properties(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # [START set_service_properties]
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
        # [END set_service_properties]

        # [START get_service_properties]
        properties = file_service.get_service_properties()
        # [END get_service_properties]

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_share_operations(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # [START fsc_create_shares]
        file_service.create_share(share_name="testshare")
        # [END fsc_create_shares]
        try:
            # [START fsc_list_shares]
            # List the shares in the file service
            my_shares = list(file_service.list_shares())

            # Print the shares
            for share in my_shares:
                print(share)
            # [END fsc_list_shares]

        finally:
            # [START fsc_delete_shares]
            file_service.delete_share(share_name="testshare")
            # [END fsc_delete_shares]

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_share_client(self, resource_group, location, storage_account, storage_account_key):
        # [START get_share_client]
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # Get a share client to interact with a specific share
        share = file_service.get_share_client("fileshare")
        # [END get_share_client]
