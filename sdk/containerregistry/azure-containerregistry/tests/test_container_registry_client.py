# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContainerRegistryClient,
    ContainerRegistryUserCredential,
)
from azure.identity import DefaultAzureCredential

from _shared.testcase import ContainerRegistryTestClass


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRegistryClient(AzureTestCase, ContainerRegistryTestClass):

    @acr_preparer()
    def test_list_repositories(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        repos = client.list_repositories()
        count = 0
        for repo in repos._repositories:
            count += 1

        assert count > 0
