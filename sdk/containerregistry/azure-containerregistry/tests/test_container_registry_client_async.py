# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import pytest
import six

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.identity.aio import DefaultAzureCredential

from asynctestcase import AsyncContainerRegistryTestClass


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
    containerregistry_resource_group="fake_rg",
)


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):

    @acr_preparer()
    async def test_list_repositories(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        repositories = client.list_repositories()

        count = 0
        prev = None
        async for repo in client.list_repositories():
            count += 1
            assert isinstance(repo, six.string_types)
            assert prev != repo
            prev = repo

        assert count > 0

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)
        self.sleep(5)

        client = self.create_registry_client(containerregistry_baseurl)

        deleted_result = await client.delete_repository("to_be_deleted")

        assert isinstance(deleted_result, DeletedRepositoryResult)
        assert len(deleted_result.deleted_registry_artifact_digests) == 10
        assert len(deleted_result.deleted_tags) == 1
        assert deleted_result.deleted_tags[0] == "to_be_deleted"

    @acr_preparer()
    async def test_delete_repository_does_not_exist(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        with pytest.raises(ResourceNotFoundError):
            deleted_result = await client.delete_repository("not_real_repo")
