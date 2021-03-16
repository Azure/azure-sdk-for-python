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
    DeletedRepositoryResult,
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

    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        deleted_result = client.delete_repository("debian")

        assert isinstance(deleted_result, DeletedRepositoryResult)
        assert len(deleted_result.deleted_registry_artifact_digests) == 1
        assert len(deleted_result.deleted_tags) == 1