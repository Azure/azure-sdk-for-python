# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import ContainerRegistryClient, ContainerRegistryUserCredential
from azure.identity import DefaultAzureCredential


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRegistryClient(AzureTestCase):
    def set_up(self, endpoint):
        return ContainerRegistryClient(
            endpoint = endpoint,
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"]
            )
        )

    @acr_preparer()
    def test_list_repositories(self, containerregistry_baseurl):
        client = self.set_up(containerregistry_baseurl)

        repos = 0
        for repo in client.list_repositories():
            repos += 1

        assert repos > 0
