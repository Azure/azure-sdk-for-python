# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import six

# from azure.containerregistry import DeleteRepositoryResult
from azure.core.exceptions import ResourceNotFoundError

from asynctestcase import AsyncContainerRegistryTestClass
from constants import TO_BE_DELETED, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_repository_names(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        count = 0
        prev = None
        async for repo in client.list_repository_names():
            count += 1
            assert isinstance(repo, six.string_types)
            assert prev != repo
            prev = repo

        assert count > 0

    @acr_preparer()
    async def test_list_repository_names_by_page(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)
        results_per_page = 2
        total_pages = 0

        repository_pages = client.list_repository_names(results_per_page=results_per_page)

        prev = None
        async for page in repository_pages.by_page():
            page_count = 0
            async for repo in page:
                assert isinstance(repo, six.string_types)
                assert prev != repo
                prev = repo
                page_count += 1
            assert page_count <= results_per_page
            total_pages += 1

        assert total_pages >= 1

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("repo")
        self.import_image(HELLO_WORLD, [TO_BE_DELETED])
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_repository(TO_BE_DELETED)

        async for repo in client.list_repository_names():
            if repo == TO_BE_DELETED:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    async def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            await client.delete_repository("not_real_repo")
