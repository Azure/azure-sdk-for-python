# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import six

from azure.containerregistry import (
    ArtifactTagProperties,
    RepositoryProperties,
    ArtifactManifestProperties,
    # RegistryArtifact,
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
    def test_get_repository_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        properties = client.get_repository_properties("library/hello-world")

        assert isinstance(properties, RepositoryProperties)
        assert properties.name == HELLO_WORLD

    @acr_preparer()
    def test_list_manifests(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        count = 0
        for manifest in client.list_manifests("library/hello-world"):
            assert isinstance(manifest, ArtifactManifestProperties)
            count += 1
        assert count > 0

    @acr_preparer()
    def test_get_manifest_properties(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        registry_artifact = client.get_manifest_properties("library/hello-world", "latest")

        assert isinstance(registry_artifact, ArtifactManifestProperties)
        assert "latest" in registry_artifact.tags
        assert registry_artifact.repository_name == "library/hello-world"

    @acr_preparer()
    def test_list_tags(self, containerregistry_anonregistry_endpoint):
        client = self.create_anon_client(containerregistry_anonregistry_endpoint)
        assert client._credential is None

        count = 0
        for tag in client.list_tags("library/hello-world"):
            count += 1
            assert isinstance(tag, ArtifactTagProperties)
        assert count > 0
