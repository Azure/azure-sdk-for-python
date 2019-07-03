# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

try:
    import settings_real as settings
except ImportError:
    import file_settings_fake as settings

from filetestcase import (
    FileTestCase,
    record
)

SOURCE_FILE = 'SampleSource.txt'


class TestHelloWorldSamples(FileTestCase):

    connection_string = settings.CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestHelloWorldSamples, self).setUp()

    def tearDown(self):
        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass

        return super(TestHelloWorldSamples, self).tearDown()

    #--Begin File Samples-----------------------------------------------------------------

    @record
    def test_create_client_with_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = file_service.get_service_properties()
        assert properties is not None

    @record
    def test_create_file_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share="myshare")

        # Create the share
        share.create_share()

        try:
            # [START get_share_properties]
            properties = share.get_share_properties()
            # [END get_share_properties]
            assert properties is not None

        finally:
            # Delete the share
            share.delete_share()

    @record
    def test_upload_file_to_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share="share")

        # Create the share
        share.create_share()

        try:
            # Instantiate the FileClient from a connection string
            # [START create_file_client]
            from azure.storage.file import FileClient
            file = FileClient.from_connection_string(self.connection_string, share="share", file_path="myfile")
            # [END create_file_client]

            # Upload a file
            with open(SOURCE_FILE, "rb") as source_file:
                file.upload_file(source_file)

        finally:
            # Delete the share
            share.delete_share()
