# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from devtools_testutils import AzureTestCase

from azure.containerregistry import (
    ContainerRegistryClient
)
from azure.identity import DefaultAzureCredential


class TestContainerRegistryClient(AzureTestCase):

    def _set_up(self):
        return self.create_client_from_credential(
            ContainerRegistryClient,
            self.get_credential(ContainerRegistryClient),
            endpoint=os.environ['CONTAINERREGISTRY_BASEURL'],
        )

    def test_list_repositories(self):
        client = self._set_up()

        repos = 0
        for repo in client.list_repositories():
            repos += 1

        assert repos > 0