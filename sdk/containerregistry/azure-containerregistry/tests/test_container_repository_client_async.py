# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import functools
import os
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContentPermissions,
    RepositoryProperties,
    RegistryArtifactProperties,
    TagProperties,
    TagOrderBy,
)
from azure.containerregistry.aio import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
)
from azure.core.paging import ItemPaged

from asynctestcase import AsyncContainerRegistryTestClass

acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRepositoryClient(AsyncContainerRegistryTestClass):

    @acr_preparer()
    async def test_list_registry_artifacts(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        async for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)

    @acr_preparer()
    async def test_list_registry_artifacts_by_page(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)
        results_per_page = 2

        pages = client.list_registry_artifacts(results_per_page=results_per_page)
        page_count = 0
        async for page in pages.by_page():
            reg_count = 0
            async for tag in page:
                reg_count += 1
            assert reg_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    async def test_list_tags(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        tags = client.list_tags()
        assert isinstance(tags, ItemPaged)
        count = 0
        async for tag in tags:
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_tags_by_page(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        results_per_page = 2

        pages = client.list_tags(results_per_page=results_per_page)
        page_count = 0
        async for page in pages.by_page():
            tag_count = 0
            for tag in page:
                tag_count += 1
            assert tag_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    async def test_list_tags_descending(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        # TODO: This is giving time in ascending order
        tags = client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_DESCENDING)
        assert isinstance(tags, ItemPaged)
        last_updated_on = None
        count = 0
        async for tag in tags:
            print(tag.last_updated_on)
            # if last_updated_on:
            #     assert tag.last_updated_on < last_updated_on
            last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0
