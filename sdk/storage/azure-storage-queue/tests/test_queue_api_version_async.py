# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
from datetime import datetime, timedelta

from azure.core.exceptions import AzureError, ResourceExistsError
from azure.storage.queue.aio import (
    QueueServiceClient,
    QueueClient
)
from _shared.testcase import GlobalStorageAccountPreparer
from _shared.asynctestcase import AsyncStorageTestCase

# ------------------------------------------------------------------------------

class StorageClientTest(AsyncStorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = '2018-03-28'

    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        service_client = QueueServiceClient(
            "https://foo.queue.core.windows.net/account",
            credential="fake_key")
        self.assertEqual(service_client.api_version, self.api_version_2)
        self.assertEqual(service_client._client._config.version, self.api_version_2)

        with pytest.raises(AttributeError):
            service_client.api_version = "foo"

        service_client = QueueServiceClient(
            "https://foo.queue.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(service_client.api_version, self.api_version_1)
        self.assertEqual(service_client._client._config.version, self.api_version_1)

        queue_client = service_client.get_queue_client("foo")
        self.assertEqual(queue_client.api_version, self.api_version_1)
        self.assertEqual(queue_client._client._config.version, self.api_version_1)

    def test_blob_client_api_version_property(self):
        queue_client = QueueClient(
            "https://foo.queue.core.windows.net/account",
            "queue_name",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(queue_client.api_version, self.api_version_1)
        self.assertEqual(queue_client._client._config.version, self.api_version_1)

        queue_client = QueueClient(
            "https://foo.queue.core.windows.net/account",
            "queue_name",
            credential="fake_key")
        self.assertEqual(queue_client.api_version, self.api_version_2)
        self.assertEqual(queue_client._client._config.version, self.api_version_2)

# ------------------------------------------------------------------------------
