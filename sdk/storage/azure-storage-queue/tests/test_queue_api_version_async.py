# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.storage.queue.aio import QueueClient, QueueServiceClient
from azure.storage.queue._shared.constants import X_MS_VERSION

from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase


# ------------------------------------------------------------------------------

class TestAsyncStorageClient(AsyncStorageRecordedTestCase):
    def setUp(self):
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = X_MS_VERSION

    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        self.setUp()
        service_client = QueueServiceClient(
            "https://foo.queue.core.windows.net/account",
            credential="fake_key")
        assert service_client.api_version == self.api_version_2
        assert service_client._client._config.version == self.api_version_2

        with pytest.raises(AttributeError):
            service_client.api_version = "foo"

        service_client = QueueServiceClient(
            "https://foo.queue.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        assert service_client.api_version == self.api_version_1
        assert service_client._client._config.version == self.api_version_1

        queue_client = service_client.get_queue_client("foo")
        assert queue_client.api_version == self.api_version_1
        assert queue_client._client._config.version == self.api_version_1

    def test_queue_client_api_version_property(self):
        self.setUp()
        queue_client = QueueClient(
            "https://foo.queue.core.windows.net/account",
            "queue_name",
            credential="fake_key",
            api_version=self.api_version_1)
        assert queue_client.api_version == self.api_version_1
        assert queue_client._client._config.version == self.api_version_1

        queue_client = QueueClient(
            "https://foo.queue.core.windows.net/account",
            "queue_name",
            credential="fake_key")
        assert queue_client.api_version == self.api_version_2
        assert queue_client._client._config.version == self.api_version_2

# ------------------------------------------------------------------------------
