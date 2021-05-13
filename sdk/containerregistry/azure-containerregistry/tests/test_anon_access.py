# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import six
from azure import containerregistry

from azure.containerregistry import (
    ArtifactTagProperties,
    RepositoryProperties,
    ArtifactManifestProperties,
    RegistryArtifact,
)

from azure.core.paging import ItemPaged
from azure.core.pipeline.transport import RequestsTransport

from testcase import ContainerRegistryTestClass
from constants import HELLO_WORLD
from preparer import acr_preparer


class TestContainerRegistryClient(ContainerRegistryTestClass):
    @acr_preparer()
    def test_list_repository_names(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

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
    def test_list_repository_names_by_page(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

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
    def test_transport_closed_only_once(self, containerregistry_anonregistry_endpoint):
        transport = RequestsTransport()
        client = self.create_anon_client(containerregistry_anonregistry_endpoint, transport=transport)
        assert client._credential is None
        with client:
            for r in client.list_repository_names():
                pass
            assert transport.session is not None

            with client.get_repository(HELLO_WORLD) as repo_client:
                assert repo_client._credential is None
                assert transport.session is not None

            for r in client.list_repository_names():
                pass
            assert transport.session is not None

    @acr_preparer()
    def test_get_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        properties = container_repository.get_properties()

        assert isinstance(properties, RepositoryProperties)
        assert properties.name == HELLO_WORLD

    @acr_preparer()
    def test_list_manifests(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        count = 0
        for manifest in container_repository.list_manifests():
            assert isinstance(manifest, ArtifactManifestProperties)
            count += 1
        assert count > 0

    @acr_preparer()
    def test_get_artifact(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        registry_artifact = container_repository.get_artifact("latest")
        assert registry_artifact._credential is None

        assert isinstance(registry_artifact, RegistryArtifact)

    @acr_preparer()
    def test_list_tags(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        container_repository = client.get_repository(HELLO_WORLD)
        assert container_repository._credential is None

        for manifest in container_repository.list_manifests():
            registry_artifact = container_repository.get_artifact(manifest.digest)
        assert registry_artifact._credential is None

        count = 0
        for tag in registry_artifact.list_tags():
            count += 1
            assert isinstance(tag, ArtifactTagProperties)
        assert count > 0
