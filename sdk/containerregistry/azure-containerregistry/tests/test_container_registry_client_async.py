# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import six

from azure.containerregistry import DeleteRepositoryResult
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import AioHttpTransport

from asynctestcase import AsyncContainerRegistryTestClass
from constants import TO_BE_DELETED, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_repository_names(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        repositories = client.list_repository_names()

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

        result = await client.delete_repository(TO_BE_DELETED)
        assert isinstance(result, DeleteRepositoryResult)
        assert result.deleted_manifests is not None
        assert result.deleted_tags is not None

        async for repo in client.list_repository_names():
            if repo == TO_BE_DELETED:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    async def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            await client.delete_repository("not_real_repo")

    @acr_preparer()
    async def test_transport_closed_only_once(self, containerregistry_endpoint):
        transport = AioHttpTransport()
        client = self.create_registry_client(containerregistry_endpoint, transport=transport)
        async with client:
            async for r in client.list_repository_names():
                pass
            assert transport.session is not None

            repo_client = client.get_repository(HELLO_WORLD)
            async with repo_client:
                assert transport.session is not None

            async for r in client.list_repository_names():
                pass
            assert transport.session is not None
