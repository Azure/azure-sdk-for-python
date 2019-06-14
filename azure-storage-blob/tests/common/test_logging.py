# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import logging

import sys
from datetime import datetime, timedelta

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from azure.storage.blob.models import ContainerPermissions, BlobPermissions
from azure.storage.blob._utils import _QueryStringConstants

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
    LogCaptured,
)

if sys.version_info >= (3,):
    from urllib.parse import parse_qs, quote
else:
    from urlparse import parse_qs
    from urllib2 import quote

_AUTHORIZATION_HEADER_NAME = 'Authorization'

class StorageLoggingTest(StorageTestCase):

    def setUp(self):
        super(StorageLoggingTest, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        self.bsc = BlobServiceClient(url, credential=credential)
        self.container_name = self.get_resource_name('utcontainer')

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_data = self.get_random_bytes(4 * 1024)
        source_blob = self.bsc.get_blob_client(self.container_name, self.source_blob_name)

        if not self.is_playback():
            self.bsc.create_container(self.container_name)
            source_blob.upload_blob(self.source_blob_data)

        # generate a SAS so that it is accessible with a URL
        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_source = BlobClient(source_blob.url, credential=sas_token)
        self.source_blob_url = sas_source.url

    def tearDown(self):
        if not self.is_playback():
            self.bsc.delete_container(self.container_name)

        return super(StorageLoggingTest, self).tearDown()

    @record
    def test_authorization_is_scrubbed_off(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        # Act
        with LogCaptured(self) as log_captured:
            container.get_container_properties(logging_enable=True)
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
        container = self.bsc.get_container_client(self.container_name)
        token = container.generate_shared_access_signature(
            permission=ContainerPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        # parse out the signed signature
        token_components = parse_qs(token)
        signed_signature = quote(token_components[_QueryStringConstants.SIGNED_SIGNATURE][0])

        sas_service = ContainerClient(container.url, credential=token)

        # Act
        with LogCaptured(self) as log_captured:
            sas_service.get_account_information(logging_enable=True)
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
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # parse out the signed signature
        token_components = parse_qs(self.source_blob_url)
        signed_signature = quote(token_components[_QueryStringConstants.SIGNED_SIGNATURE][0])

        # Act
        with LogCaptured(self) as log_captured:
            dest_blob.copy_blob_from_url(
                self.source_blob_url, requires_sync=True, logging_enable=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            self.assertTrue(_QueryStringConstants.SIGNED_SIGNATURE in log_as_str)
            self.assertFalse(signed_signature in log_as_str)

            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            self.assertTrue(_AUTHORIZATION_HEADER_NAME in log_as_str)
            self.assertFalse('SharedKey' in log_as_str)
