# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import datetime

from azure.ai.projects.models import SASTokenCredential
from azure.core.credentials import TokenCredential, AccessToken
from azure.core.exceptions import HttpResponseError

from connection_test_base import ConnectionsTestBase


# The test class name needs to start with "Test" to get collected by pytest
class TestConnections(ConnectionsTestBase):

    def test_get_connection(self, **kwargs):
        project_client = self.get_sync_client(**kwargs)
        pass

    def test_get_default_connection(self, **kwargs):
        pass

    def test_list_connections(self, **kwargs):
        pass