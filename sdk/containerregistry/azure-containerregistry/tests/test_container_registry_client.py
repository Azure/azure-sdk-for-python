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
    ContainerRegistryClient,
    DeletedRepositoryResult,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.identity import DefaultAzureCredential

from testcase import ContainerRegistryTestClass


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRegistryClient(ContainerRegistryTestClass):

    @acr_preparer()
    def test_list_repositories(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        repositories = client.list_repositories()
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
    def test_list_repositories_by_page(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)
        page_size = 2
        total_pages = 0

        repository_pages = client.list_repositories(page_size=page_size)

        prev = None
        for page in repository_pages.by_page():
            page_count = 0
            for repo in page:
                assert isinstance(repo, six.string_types)
                assert prev != repo
                prev = repo
                page_count += 1
            assert page_count <= page_size
            total_pages += 1

        assert total_pages > 1

    @pytest.mark.skip("Don't want to delete for now")
    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        deleted_result = client.delete_repository("debian")

        assert isinstance(deleted_result, DeletedRepositoryResult)
        assert len(deleted_result.deleted_registry_artifact_digests) == 1
        assert len(deleted_result.deleted_tags) == 1

    @pytest.mark.skip("Don't want to for now")

    @acr_preparer()
    def test_delete_repository_does_not_exist(self, containerregistry_baseurl):
        client = self.create_registry_client(containerregistry_baseurl)

        with pytest.raises(ResourceNotFoundError):
            deleted_result = client.delete_repository("not_real_repo")
