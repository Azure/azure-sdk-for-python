# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import six

from azure.core.exceptions import ClientAuthenticationError
from azure.core.paging import ItemPaged
from azure.containerregistry import (
    ArtifactTagProperties,
    RepositoryProperties,
    ArtifactManifestProperties,
    ContainerRegistryClient,
)

from testcase import ContainerRegistryTestClass
from constants import HELLO_WORLD
from preparer import acr_preparer
from devtools_testutils import recorded_by_proxy


class TestContainerRegistryClient(ContainerRegistryTestClass):
    @acr_preparer()
    @recorded_by_proxy
    def test_list_repository_names(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
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
    @recorded_by_proxy
    def test_list_repository_names_by_page(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
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

            assert total_pages >= 1

    @acr_preparer()
    @recorded_by_proxy
    def test_get_repository_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            properties = client.get_repository_properties(HELLO_WORLD)

            assert isinstance(properties, RepositoryProperties)
            assert properties.name == HELLO_WORLD

    @acr_preparer()
    @recorded_by_proxy
    def test_list_manifest_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            count = 0
            for manifest in client.list_manifest_properties(HELLO_WORLD):
                assert isinstance(manifest, ArtifactManifestProperties)
                count += 1
            assert count > 0

    @acr_preparer()
    @recorded_by_proxy
    def test_get_manifest_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            registry_artifact = client.get_manifest_properties(HELLO_WORLD, "latest")

            assert isinstance(registry_artifact, ArtifactManifestProperties)
            assert "latest" in registry_artifact.tags
            assert registry_artifact.repository_name == HELLO_WORLD

    @acr_preparer()
    @recorded_by_proxy
    def test_list_tag_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            count = 0
            for tag in client.list_tag_properties(HELLO_WORLD):
                count += 1
                assert isinstance(tag, ArtifactTagProperties)
            assert count > 0

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_repository(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            with pytest.raises(ClientAuthenticationError):
                client.delete_repository(HELLO_WORLD)

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_tag(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            with pytest.raises(ClientAuthenticationError):
                client.delete_tag(HELLO_WORLD, "latest")

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_manifest(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            assert client._credential is None

            with pytest.raises(ClientAuthenticationError):
                client.delete_manifest(HELLO_WORLD, "latest")

    @acr_preparer()
    @recorded_by_proxy
    def test_update_repository_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            properties = client.get_repository_properties(HELLO_WORLD)

            with pytest.raises(ClientAuthenticationError):
                client.update_repository_properties(HELLO_WORLD, properties, can_delete=True)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_tag_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            properties = client.get_tag_properties(HELLO_WORLD, "latest")

            with pytest.raises(ClientAuthenticationError):
                client.update_tag_properties(HELLO_WORLD, "latest", properties, can_delete=True)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_manifest_properties(self, containerregistry_anonregistry_endpoint):
        if not self.is_public_endpoint(containerregistry_anonregistry_endpoint):
            pytest.skip("Not a public endpoint")

        with self.create_anon_client(containerregistry_anonregistry_endpoint) as client:
            properties = client.get_manifest_properties(HELLO_WORLD, "latest")

            with pytest.raises(ClientAuthenticationError):
                client.update_manifest_properties(HELLO_WORLD, "latest", properties, can_delete=True)


def test_set_api_version():
    containerregistry_endpoint="https://fake_url.azurecr.io"

    with ContainerRegistryClient(endpoint=containerregistry_endpoint, audience="https://microsoft.com") as client:
        assert client._client._config.api_version == "2021-07-01"

    with ContainerRegistryClient(
        endpoint=containerregistry_endpoint, audience="https://microsoft.com", api_version = "2019-08-15-preview"
    ) as client:
        assert client._client._config.api_version == "2019-08-15-preview"

    with pytest.raises(ValueError):
        with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, audience="https://microsoft.com", api_version = "2019-08-15"
        ) as client:
            pass
