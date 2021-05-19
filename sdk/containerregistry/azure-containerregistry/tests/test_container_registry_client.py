# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import six

# from azure.containerregistry import DeleteRepositoryResult
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.core.pipeline.transport import RequestsTransport

from testcase import ContainerRegistryTestClass
from constants import TO_BE_DELETED, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(ContainerRegistryTestClass):
    @acr_preparer()
    def test_list_repository_names(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        repositories = client.list_repository_names()
        assert isinstance(repositories, ItemPaged)

        count = 0
        prev = None
        for repo in repositories:
            count += 1
            assert isinstance(repo, six.string_types)
            assert prev != repo
            prev = repo

        assert count > 0

    @acr_preparer()
    def test_list_repository_names_by_page(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)
        results_per_page = 2
        total_pages = 0

        repository_pages = client.list_repository_names(results_per_page=results_per_page)

        prev = None
        for page in repository_pages.by_page():
            page_count = 0
            for repo in page:
                assert isinstance(repo, six.string_types)
                assert prev != repo
                prev = repo
                page_count += 1
            assert page_count <= results_per_page
            total_pages += 1

        assert total_pages > 1

    @acr_preparer()
    def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_image(HELLO_WORLD, [TO_BE_DELETED])
        client = self.create_registry_client(containerregistry_endpoint)

        client.delete_repository(TO_BE_DELETED)

        for repo in client.list_repository_names():
            if repo == TO_BE_DELETED:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            client.delete_repository("not_real_repo")
