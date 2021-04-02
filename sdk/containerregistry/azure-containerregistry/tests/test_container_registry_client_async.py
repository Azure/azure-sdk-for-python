# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import six

from devtools_testutils import AzureTestCase

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from preparer import acr_preparer


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
        repository = self.get_resource_name("repo")
        self._import_tag_to_be_deleted(
            containerregistry_baseurl, resource_group=containerregistry_resource_group, repository=repository
        )
        client = self.create_registry_client(containerregistry_baseurl)

        await client.delete_repository(repository)
        self.sleep(5)

        async for repo in client.list_repositories():
            if repo == repository:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    async def test_delete_repository_does_not_exist(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        with pytest.raises(ResourceNotFoundError):
            deleted_result = await client.delete_repository("not_real_repo")
