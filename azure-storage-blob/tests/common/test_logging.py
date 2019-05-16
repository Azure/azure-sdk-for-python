# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

pytestmark = pytest.mark.skip

import sys
from datetime import datetime, timedelta

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    #ContainerPermissions,  # TODO
    #BlobPermissions,
)
# from azure.storage.common._constants import (
#     _AUTHORIZATION_HEADER_NAME,
# )
# from azure.storage.common.sharedaccesssignature import (
#     _QueryStringConstants,
# )
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
    LogCaptured,
)

if sys.version_info >= (3,):
    from urllib.parse import parse_qs
else:
    from urlparse import parse_qs


class StorageLoggingTest(StorageTestCase):

    def setUp(self):
        super(StorageLoggingTest, self).setUp()

        self.bs = self._create_storage_service(BlockBlobService, self.settings)
        self.container_name = self.get_resource_name('utcontainer')

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_data = self.get_random_bytes(4 * 1024)

        if not self.is_playback():
            self.bs.create_container(self.container_name)
            self.bs.create_blob_from_bytes(self.container_name, self.source_blob_name, self.source_blob_data)

        # generate a SAS so that it is accessible with a URL
        sas_token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            self.source_blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        self.source_blob_url = self.bs.make_blob_url(self.container_name, self.source_blob_name, sas_token=sas_token)

    def tearDown(self):
        if not self.is_playback():
            self.bs.delete_container(self.container_name)

        return super(StorageLoggingTest, self).tearDown()

    @record
    def test_authorization_is_scrubbed_off(self):
        # Act
        with LogCaptured(self) as log_captured:
            self.bs.exists(self.container_name)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            self.assertTrue(_AUTHORIZATION_HEADER_NAME in log_as_str)
            self.assertFalse('SharedKey' in log_as_str)

    @record
    def test_sas_signature_is_scrubbed_off(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token = self.bs.generate_container_shared_access_signature(
            self.container_name,
            permission=ContainerPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        # parse out the signed signature
        token_components = parse_qs(token)
        signed_signature = token_components[_QueryStringConstants.SIGNED_SIGNATURE][0]

        bs_with_sas = BlockBlobService(account_name=self.settings.STORAGE_ACCOUNT_NAME, sas_token=token,
                                       protocol=self.settings.PROTOCOL)

        # Act
        with LogCaptured(self) as log_captured:
            bs_with_sas.get_blob_account_information(self.container_name)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            self.assertTrue(_QueryStringConstants.SIGNED_SIGNATURE in log_as_str)
            self.assertFalse(signed_signature in log_as_str)

    @record
    def test_copy_source_sas_is_scrubbed_off(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        dest_blob_name = self.get_resource_name('destblob')

        # parse out the signed signature
        token_components = parse_qs(self.source_blob_url)
        signed_signature = token_components[_QueryStringConstants.SIGNED_SIGNATURE][0]

        # Act
        with LogCaptured(self) as log_captured:
            self.bs.copy_blob(self.container_name, dest_blob_name, self.source_blob_url, requires_sync=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            self.assertTrue(_QueryStringConstants.SIGNED_SIGNATURE in log_as_str)
            self.assertFalse(signed_signature in log_as_str)

            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            self.assertTrue(_AUTHORIZATION_HEADER_NAME in log_as_str)
            self.assertFalse('SharedKey' in log_as_str)
