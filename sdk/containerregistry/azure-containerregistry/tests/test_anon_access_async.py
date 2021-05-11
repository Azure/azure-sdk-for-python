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
from azure.containerregistry.aio import RegistryArtifact

from azure.core.pipeline.transport import AioHttpTransport

from asynctestcase import AsyncContainerRegistryTestClass
from constants import HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_repository_names(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        count = 0
        prev = None
        async for repo in client.list_repository_names():
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
    async def test_transport_closed_only_once(self, containerregistry_anonregistry_endpoint):
        transport = AioHttpTransport()
        client = self.create_anon_client(containerregistry_anonregistry_endpoint, transport=transport)
        assert client._credential is None

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

    @acr_preparer()
    async def test_get_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        properties = await container_repository.get_properties()

        assert isinstance(properties, RepositoryProperties)
        assert properties.name == HELLO_WORLD

    @acr_preparer()
    async def test_list_manifests(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        count = 0
        async for manifest in container_repository.list_manifests():
            assert isinstance(manifest, ArtifactManifestProperties)
            count += 1
        assert count > 0

    @acr_preparer()
    async def test_get_artifact(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        registry_artifact = container_repository.get_artifact("latest")
        assert registry_artifact._credential is None

        assert isinstance(registry_artifact, RegistryArtifact)

    @acr_preparer()
    async def test_list_tags(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        async for manifest in container_repository.list_manifests():
            registry_artifact = container_repository.get_artifact(manifest.digest)
        assert registry_artifact._credential is None

        count = 0
        async for tag in registry_artifact.list_tags():
            count += 1
            assert isinstance(tag, ArtifactTagProperties)
        assert count > 0
