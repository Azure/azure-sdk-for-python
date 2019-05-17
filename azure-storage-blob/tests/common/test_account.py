# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

pytestmark = pytest.mark.xfail
import unittest
from datetime import datetime, timedelta

import requests

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
# from azure.storage.common import (
#     CloudStorageAccount,
#     ResourceTypes,
#     AccountPermissions,
#     Services,
# )
from azure.storage.blob.constants import (
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY
)

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
    not_for_emulator,
)


# ------------------------------------------------------------------------------


class StorageAccountTest(StorageTestCase):
    def setUp(self):
        super(StorageAccountTest, self).setUp()
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'

        if self.settings.IS_EMULATED:
            self.account_name = DEV_ACCOUNT_NAME
            self.account_key = DEV_ACCOUNT_KEY
            self.protocol = "http"
            self.account = CloudStorageAccount(DEV_ACCOUNT_NAME, DEV_ACCOUNT_KEY, is_emulated=True)
        else:
            self.account_name = self.settings.STORAGE_ACCOUNT_NAME
            self.account_key = self.settings.STORAGE_ACCOUNT_KEY
            self.account = CloudStorageAccount(self.account_name, self.account_key)
            self.protocol = self.settings.PROTOCOL

    # --Helpers-----------------------------------------------------------------
    def validate_service(self, service, type):
        self.assertIsNotNone(service)
        self.assertIsInstance(service, type)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.account_key, self.account_key)

    # --Test cases --------------------------------------------------------
    def test_create_service_no_key(self):
        # Arrange

        # Act
        bad_account = CloudStorageAccount('', '')
        with self.assertRaises(ValueError):
            service = bad_account.create_block_blob_service()

            # Assert

    def test_create_account_sas(self):
        # Arrange

        # Act
        sas_account = CloudStorageAccount(self.account_name, sas_token=self.sas_token)
        service = sas_account.create_block_blob_service()

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertIsNone(service.account_key)
        self.assertEqual(service.sas_token, self.sas_token)

    def test_create_account_sas_and_key(self):
        # Arrange

        # Act
        account = CloudStorageAccount(self.account_name, self.account_key, self.sas_token)
        service = account.create_block_blob_service()

        # Assert
        self.validate_service(service, BlockBlobService)

    def test_create_account_emulated(self):
        # Arrange

        # Act
        account = CloudStorageAccount(is_emulated=True)
        service = account.create_block_blob_service()

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, 'devstoreaccount1')
        self.assertIsNotNone(service.account_key)

    @record
    def test_generate_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token = self.account.generate_shared_access_signature(
            Services.BLOB,
            ResourceTypes.OBJECT,
            AccountPermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
        )

        service = self.account.create_block_blob_service()
        data = b'shared access signature with read permission on blob'
        container_name = self.get_resource_name("container")
        blob_name = 'blob1.txt'

        try:
            service.create_container(container_name)
            service.create_blob_from_bytes(container_name, blob_name, data)

            # Act
            url = service.make_blob_url(
                container_name,
                blob_name,
                sas_token=token,
            )
            response = requests.get(url)

            # Assert
            self.assertTrue(response.ok)
            self.assertEqual(data, response.content)
        finally:
            service.delete_container(container_name)

    @record
    def test_account_sas_with_question_mark_prefix(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token = '?' + self.account.generate_shared_access_signature(
            Services.BLOB,
            ResourceTypes.OBJECT + ResourceTypes.CONTAINER,
            AccountPermissions.READ + AccountPermissions.WRITE + AccountPermissions.DELETE + AccountPermissions.CREATE,
            datetime.utcnow() + timedelta(hours=1),
        )

        service = BlockBlobService(self.account_name, sas_token=token, is_emulated=self.settings.IS_EMULATED)
        data = b'shared access signature with read/write permission on blob'
        container_name = self.get_resource_name("container")
        blob_name = 'blob1.txt'

        try:
            # Act
            service.create_container(container_name)
            service.create_blob_from_bytes(container_name, blob_name, data)
            blob = service.get_blob_to_bytes(container_name, blob_name)

            # Assert
            self.assertIsNotNone(blob)
            self.assertEqual(data, blob.content)
        finally:
            service.delete_container(container_name)

    @record
    def test_generate_account_sas_with_multiple_permissions(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Validate both + and | generate the same permissions
        permissions = AccountPermissions.READ + AccountPermissions.WRITE
        permissions_or = AccountPermissions.READ | AccountPermissions.WRITE
        self.assertEqual(str(permissions), str(permissions_or))

        # Arrange
        token = self.account.generate_shared_access_signature(
            Services.BLOB,
            ResourceTypes.OBJECT,
            permissions,
            datetime.utcnow() + timedelta(hours=1),
        )

        service_with_key = self.account.create_block_blob_service()
        service_with_sas = BlockBlobService(account_name=self.account_name, sas_token=token, is_emulated=self.settings.IS_EMULATED)
        data = b'shared access signature with read/write permission on blob'
        container_name = self.get_resource_name("container")
        blob_name = 'blob1.txt'

        try:
            # Act Write
            service_with_key.create_container(container_name)

            # wait a few seconds to allow the container to be created
            self.sleep(5)

            resp = service_with_sas.create_blob_from_text(container_name, blob_name, data)

            # Assert Write
            self.assertIsNotNone(resp.etag)
            self.assertIsNotNone(resp.last_modified)

            # Act Read
            blob = service_with_sas.get_blob_to_bytes(container_name, blob_name)

            # Assert Read
            self.assertIsNotNone(blob.content)
            self.assertEqual(data, blob.content)

        finally:
            service_with_key.delete_container(container_name)

    @record
    def test_generate_account_sas_with_multiple_services(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token = self.account.generate_shared_access_signature(
            Services.BLOB + Services.TABLE,
            ResourceTypes.SERVICE + ResourceTypes.OBJECT,
            AccountPermissions.READ + AccountPermissions.WRITE,
            datetime.utcnow() + timedelta(hours=1),
        )
        self.assertTrue('ss=bt' in token)

        # Act Table
        # this needs to be hard coded as the table package is no longer maintained here
        url = '{}://{}/?restype=service&comp=properties&{}'.format(
            self.protocol,
            self.account_name + ".table.core.windows.net" if not self.settings.IS_EMULATED else "127.0.0.1:10002/" + DEV_ACCOUNT_NAME,
            token,
        )
        response = requests.get(url)

        # Assert Table
        self.assertTrue(response.ok)

        # Act Blob
        service_with_key = self.account.create_block_blob_service()
        service_with_sas = BlockBlobService(account_name=self.account_name, sas_token=token, is_emulated=self.settings.IS_EMULATED)
        data = b'shared access signature with read/write permission on blob'
        container_name = self.get_resource_name("container")
        blob_name = 'blob1.txt'

        try:
            # Act Write
            service_with_key.create_container(container_name)
            resp = service_with_sas.create_blob_from_text(container_name, blob_name, data)

            # Assert Write
            self.assertIsNotNone(resp.etag)
            self.assertIsNotNone(resp.last_modified)

            # Act Read
            blob = service_with_sas.get_blob_to_bytes(container_name, blob_name)

            # Assert Read
            self.assertIsNotNone(blob.content)
            self.assertEqual(data, blob.content)

        finally:
            service_with_key.delete_container(container_name)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
