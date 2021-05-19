# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import six

from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
    ArtifactTagProperties,
)

from azure.core.async_paging import AsyncItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from constants import HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_repository_names(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        repositories = client.list_repository_names()
        assert isinstance(repositories, AsyncItemPaged)

        count = 0
        prev = None
        async for repo in repositories:
            count += 1
            assert isinstance(repo, six.string_types)
            assert prev != repo
            prev = repo

        assert count > 0

    @acr_preparer()
    async def test_list_repository_names_by_page(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

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
    async def test_get_repository_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        properties = await client.get_repository_properties("library/alpine")

        assert isinstance(properties, RepositoryProperties)
        assert properties.name == "library/alpine"

    @acr_preparer()
    async def test_list_manifests(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        count = 0
        async for manifest in client.list_manifests("library/alpine"):
            assert isinstance(manifest, ArtifactManifestProperties)
            count += 1
        assert count > 0

    @acr_preparer()
    async def test_get_manifest_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        registry_artifact = await client.get_manifest_properties("library/alpine", "latest")

        assert isinstance(registry_artifact, ArtifactManifestProperties)
        assert "latest" in registry_artifact.tags
        assert registry_artifact.repository_name == "library/alpine"

    @acr_preparer()
    async def test_list_tags(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        count = 0
        async for tag in client.list_tags("library/alpine"):
            count += 1
            assert isinstance(tag, ArtifactTagProperties)
        assert count > 0
