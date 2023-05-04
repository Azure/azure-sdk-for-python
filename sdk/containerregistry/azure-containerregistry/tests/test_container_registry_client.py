# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
import six
import hashlib
import json
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock
from typing import Optional, Iterator, Any, MutableMapping
from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
    ArtifactManifestOrder,
    ArtifactTagProperties,
    ArtifactTagOrder,
    ContainerRegistryClient,
    ManifestDigestValidationError,
)
from azure.containerregistry._helpers import DOCKER_MANIFEST, OCI_IMAGE_MANIFEST, DEFAULT_CHUNK_SIZE
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError, HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineRequest
from azure.identity import AzureAuthorityHosts
from testcase import ContainerRegistryTestClass, get_authority, get_audience
from constants import HELLO_WORLD, ALPINE, BUSYBOX, DOES_NOT_EXIST
from preparer import acr_preparer
from devtools_testutils import recorded_by_proxy


class TestContainerRegistryClient(ContainerRegistryTestClass):
    @acr_preparer()
    @recorded_by_proxy
    def test_list_repository_names(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
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
    def test_list_repository_names_by_page(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
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
    def test_delete_repository(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [repo])
        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_repository(repo)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                client.get_repository_properties(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_repository(DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy
    def test_get_repository_properties(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = client.get_repository_properties(ALPINE)
            assert isinstance(properties, RepositoryProperties)
            assert properties.name == ALPINE

    @acr_preparer()
    @recorded_by_proxy
    def test_update_repository_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])
        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = self.set_all_properties(RepositoryProperties(), False)
            received = client.update_repository_properties(repo, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = client.update_repository_properties(repo, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_repository_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            received = client.update_repository_properties(
                repo, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = client.update_repository_properties(
                repo, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_list_registry_artifacts(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            count = 0
            for artifact in client.list_manifest_properties(BUSYBOX):
                assert isinstance(artifact, ArtifactManifestProperties)
                assert isinstance(artifact.created_on, datetime)
                assert isinstance(artifact.last_updated_on, datetime)
                assert artifact.repository_name == BUSYBOX
                assert artifact.fully_qualified_reference in self.create_fully_qualified_reference(containerregistry_endpoint, BUSYBOX, artifact.digest)
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy
    def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            results_per_page = 2

            pages = client.list_manifest_properties(BUSYBOX, results_per_page=results_per_page)
            page_count = 0
            for page in pages.by_page():
                reg_count = 0
                for tag in page:
                    reg_count += 1
                assert reg_count <= results_per_page
                page_count += 1

            assert page_count >= 1

    @acr_preparer()
    @recorded_by_proxy
    def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            for artifact in client.list_manifest_properties(BUSYBOX, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING):
                if prev_last_updated_on:
                    assert artifact.last_updated_on < prev_last_updated_on
                prev_last_updated_on = artifact.last_updated_on
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy
    def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            for artifact in client.list_manifest_properties(BUSYBOX, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_ASCENDING):
                if prev_last_updated_on:
                    assert artifact.last_updated_on > prev_last_updated_on
                prev_last_updated_on = artifact.last_updated_on
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy
    def test_get_manifest_properties(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = client.get_manifest_properties(ALPINE, "latest")
            assert isinstance(properties, ArtifactManifestProperties)
            assert properties.repository_name == ALPINE
            assert properties.fully_qualified_reference in self.create_fully_qualified_reference(containerregistry_endpoint, ALPINE, properties.digest)

    @acr_preparer()
    @recorded_by_proxy
    def test_get_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            manifest = client.get_manifest_properties(ALPINE, "latest")
            invalid_digest = manifest.digest[:-10] + u"a" * 10

            with pytest.raises(ResourceNotFoundError):
                client.get_manifest_properties(ALPINE, invalid_digest)
            with pytest.raises(ResourceNotFoundError):
                client.get_manifest_properties(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = self.set_all_properties(ArtifactManifestProperties(), False)
            received = client.update_manifest_properties(repo, tag, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = client.update_manifest_properties(repo, tag, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_manifest_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            received = client.update_manifest_properties(
                repo, tag, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = client.update_manifest_properties(
                repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_get_tag_properties(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = client.get_tag_properties(ALPINE, "latest")
            assert isinstance(properties, ArtifactTagProperties)
            assert properties.name == "latest"

    @acr_preparer()
    @recorded_by_proxy
    def test_get_tag_properties_does_not_exist(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            with pytest.raises(ResourceNotFoundError):
                client.get_tag_properties(DOES_NOT_EXIST, DOES_NOT_EXIST)
            with pytest.raises(ResourceNotFoundError):
                client.get_tag_properties(ALPINE, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = self.set_all_properties(ArtifactTagProperties(), False)
            received = client.update_tag_properties(repo, tag, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = client.update_tag_properties(repo, tag, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_update_tag_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            received = client.update_tag_properties(
                repo, tag, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = client.update_tag_properties(
                repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_list_tag_properties(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        with self.create_registry_client(containerregistry_endpoint) as client:
            count = 0
            for tag in client.list_tag_properties(ALPINE):
                assert f"{ALPINE}:{tag.name}" in tags
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy
    def test_list_tag_properties_order_descending(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            for tag in client.list_tag_properties(ALPINE, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING):
                assert f"{ALPINE}:{tag.name}" in tags
                if prev_last_updated_on:
                    assert tag.last_updated_on < prev_last_updated_on
                prev_last_updated_on = tag.last_updated_on
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy
    def test_list_tag_properties_order_ascending(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            for tag in client.list_tag_properties(ALPINE, order_by=ArtifactTagOrder.LAST_UPDATED_ON_ASCENDING):
                assert f"{ALPINE}:{tag.name}" in tags
                if prev_last_updated_on:
                    assert tag.last_updated_on > prev_last_updated_on
                prev_last_updated_on = tag.last_updated_on
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_tag(repo, tag)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                client.get_tag_properties(repo, tag)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_tag(DOES_NOT_EXIST, DOES_NOT_EXIST)
            client.delete_tag(ALPINE, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_manifest(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_manifest(repo, tag)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                client.get_manifest_properties(repo, tag)

            # Cleanup
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_delete_manifest_does_not_exist(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            manifest = client.get_manifest_properties(ALPINE, "latest")
            invalid_digest = manifest.digest[:-10] + u"a" * 10

            client.delete_manifest(ALPINE, invalid_digest)
            with pytest.raises(ResourceNotFoundError):
                client.delete_manifest(ALPINE, DOES_NOT_EXIST)
            with pytest.raises(ResourceNotFoundError):
                client.delete_manifest(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy
    def test_expiration_time_parsing(self, containerregistry_endpoint):
        from azure.containerregistry._authentication_policy import ContainerRegistryChallengePolicy
        with self.create_registry_client(containerregistry_endpoint) as client:
            for repo in client.list_repository_names():
                pass

            for policy in client._client._client._pipeline._impl_policies:
                if isinstance(policy, ContainerRegistryChallengePolicy):
                    policy._exchange_client._expiration_time = 0
                    break

            count = 0
            for repo in client.list_repository_names():
                count += 1

            assert count >= 1

    # Live only, the fake credential doesn't check auth scope the same way
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_construct_container_registry_client(self, **kwargs):
        containerregistry_endpoint = kwargs.pop("containerregistry_endpoint")
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority)

        with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, credential=credential, audience="https://microsoft.com"
        ) as client:
            with pytest.raises(ClientAuthenticationError):
                properties = client.get_repository_properties(HELLO_WORLD)
            
    @acr_preparer()
    @recorded_by_proxy
    def test_get_misspell_property(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            properties = client.get_repository_properties(ALPINE)
            
            with pytest.warns(DeprecationWarning):
                last_udpated_on = properties.last_udpated_on
            last_updated_on = properties.last_updated_on
            assert last_udpated_on == last_updated_on

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_json(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_json, media_type=DOCKER_MANIFEST)
                digest = client.set_manifest(repo, manifest_json)

            response = client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_json_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)
            
            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_json, tag=tag, media_type=DOCKER_MANIFEST)
                digest = client.set_manifest(repo, manifest_json, tag=tag)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST

            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_stream(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream)

            response = client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_stream_without_spaces(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest_without_spaces.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream)

            response = client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_stream_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)
            
            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream, tag=tag)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST
            
            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy
    def test_set_oci_manifest_stream_without_spaces_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest_without_spaces.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_oci_manifest_prerequisites(repo, client)
            
            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream, tag=tag)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST
            
            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_stream(self, containerregistry_endpoint):
        repo = "library/hello-world"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_stream)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)

            response = client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_stream_without_spaces(self, containerregistry_endpoint):
        repo = "library/hello-world"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest_without_spaces.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_stream)
                manifest_stream.seek(0)
                digest = client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)

            response = client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_stream_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_stream, tag=tag)
                digest = client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_stream_without_spaces_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest_without_spaces.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_stream, tag=tag)
                digest = client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_json(self, containerregistry_endpoint):
        repo = "library/hello-world"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_json)
                digest = client.set_manifest(repo, manifest_json, media_type=DOCKER_MANIFEST)
            
            response = client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            client.delete_manifest(repo, digest)
            client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_set_docker_manifest_json_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        with self.create_registry_client(containerregistry_endpoint) as client:
            self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    client.set_manifest(repo, manifest_json, tag=tag)
                digest = client.set_manifest(repo, manifest_json, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = client.get_manifest_properties(repo, digest).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            client.delete_manifest(repo, digest)
            client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy
    def test_upload_blob(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        blob = "654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", blob)

        with self.create_registry_client(containerregistry_endpoint) as client:
            # Act
            with open(path, "rb") as data:
                digest, blob_size = client.upload_blob(repo, data)

            # Assert
            blob_content = b""
            stream = client.download_blob(repo, digest)
            for chunk in stream:
                blob_content += chunk
            assert len(blob_content) == blob_size

            client.delete_blob(repo, digest)
            client.delete_repository(repo)

    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy
    def test_upload_large_blob_in_chunk(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        with self.create_registry_client(containerregistry_endpoint) as client:
            # Test blob upload and download in equal size chunks
            blob_size = DEFAULT_CHUNK_SIZE * 1024 # 4GB
            data = b'\x00' * int(blob_size)
            digest, size = client.upload_blob(repo, BytesIO(data))
            assert size == blob_size

            stream = client.download_blob(repo, digest)
            size = 0
            with open("text1.txt", "wb") as file:
                for chunk in stream:
                    size += file.write(chunk)
            assert size == blob_size

            client.delete_blob(repo, digest)

            # Test blob upload and download in unequal size chunks
            blob_size = DEFAULT_CHUNK_SIZE * 1024 + 20
            data = b'\x00' * int(blob_size)
            digest, size = client.upload_blob(repo, BytesIO(data))
            assert size == blob_size

            stream = client.download_blob(repo, digest)
            size = 0
            with open("text2.txt", "wb") as file:
                for chunk in stream:
                    size += file.write(chunk)
            assert size == blob_size

            client.delete_blob(repo, digest)

            # Cleanup
            client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy
    def test_delete_blob_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        hash_value = hashlib.sha256(b"test").hexdigest()
        digest = f"sha256:{hash_value}"
        with self.create_registry_client(containerregistry_endpoint) as client:
            client.delete_blob(repo, digest)

    @acr_preparer()
    @recorded_by_proxy
    def test_set_audience(self, containerregistry_endpoint):
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority=authority)
        
        with ContainerRegistryClient(endpoint=containerregistry_endpoint, credential=credential) as client:
            for repo in client.list_repository_names():
                pass

        valid_audience = get_audience(authority)
        with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, credential=credential, audience=valid_audience
        ) as client:
            for repo in client.list_repository_names():
                pass

        if valid_audience == get_audience(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD):
            invalid_audience = get_audience(AzureAuthorityHosts.AZURE_GOVERNMENT)
            with ContainerRegistryClient(
                endpoint=containerregistry_endpoint, credential=credential, audience=invalid_audience
            ) as client:
                with pytest.raises(ClientAuthenticationError):
                    for repo in client.list_repository_names():
                        pass

    @acr_preparer()
    @recorded_by_proxy
    def test_list_tags_in_empty_repo(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            # cleanup tags in ALPINE repo
            for tag in client.list_tag_properties(ALPINE):
                client.delete_tag(ALPINE, tag.name)
            
            response = client.list_tag_properties(ALPINE)
            if response is not None:
                for tag in response:
                    pass
    
    @acr_preparer()
    @recorded_by_proxy
    def test_list_manifests_in_empty_repo(self, containerregistry_endpoint):
        with self.create_registry_client(containerregistry_endpoint) as client:
            # cleanup manifests in ALPINE repo
            for tag in client.list_tag_properties(ALPINE):
                client.delete_manifest(ALPINE, tag.name)
            response = client.list_manifest_properties(ALPINE)
            if response is not None:
                for manifest in response:
                    pass


class TestContainerRegistryClientUnitTests:
    containerregistry_endpoint="https://fake_url.azurecr.io"
    
    def text(self, encoding: Optional[str] = None) -> str:
            return '{"hello": "world"}'

    def test_manifest_digest_validation(self):        
        JSON = MutableMapping[str, Any]
            
        def send_in_set_manifest(request: PipelineRequest, **kwargs) -> MagicMock:
            content_digest = hashlib.sha256(b"hello world").hexdigest()
            return MagicMock(
                status_code=201,
                headers={"Docker-Content-Digest": content_digest},
                content_type="application/json; charset=utf-8",
                text=self.text
        )
            
        def read() -> bytes:
            return b'{"hello": "world"}'
        
        def json() -> JSON:
            return {"hello": "world"}
        
        def send_in_get_manifest(request: PipelineRequest, **kwargs) -> MagicMock:
            content_digest = hashlib.sha256(b"hello world").hexdigest()
            content_type = "application/vnd.oci.image.manifest.v1+json"
            return MagicMock(
                status_code=200,
                headers={"Docker-Content-Digest": content_digest, "Content-Type": content_type},
                read=read,
                json=json
        )
            
        with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MagicMock(send=send_in_set_manifest)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                manifest = {"hello": "world"}
                client.set_manifest("test-repo", manifest)
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."
            
        with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint,
            transport = MagicMock(send=send_in_get_manifest)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                digest = hashlib.sha256(b"hello world").hexdigest()
                client.get_manifest("test-repo", f"sha256:{digest}")
            assert str(exp.value) == "The content of retrieved manifest digest does not match the requested digest."
                
            with pytest.raises(ManifestDigestValidationError) as exp:
                client.get_manifest("test-repo", "test-tag")
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."

    def test_blob_digest_validation(self):       
        def send_in_upload_blob(request: PipelineRequest, **kwargs) -> MagicMock:
            if request.method == "PUT":
                content_digest = hashlib.sha256(b"hello world").hexdigest()
                return MagicMock(
                    status_code=201,
                    headers={"Docker-Content-Digest": content_digest},
                    content_type="application/json; charset=utf-8",
                    text=self.text
                )
            else:
                return MagicMock(
                    status_code=202,
                    headers={"Location": "/v2/test-repo/blobs/uploads/fake_location"},
                    content_type="application/json; charset=utf-8",
                    text=self.text
                )
        
        def iter_bytes() -> Iterator[bytes]:
            yield b'{"hello": "world"}'
        
        def send_in_download_blob(request: PipelineRequest, **kwargs) -> MagicMock:
            return MagicMock(
                status_code=206,
                headers={"Content-Range": "bytes 0-27/28", "Content-Length": "28"},
                content_type="application/json; charset=utf-8",
                text=self.text,
                iter_bytes=iter_bytes
            )
            
        with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MagicMock(send=send_in_upload_blob)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                client.upload_blob("test-repo", BytesIO(b'{"hello": "world"}'))
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."
            
        with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MagicMock(send=send_in_download_blob)
        ) as client:
            digest = hashlib.sha256(b"hello world").hexdigest()
            stream = client.download_blob("test-repo", f"sha256:{digest}")
            with pytest.raises(ManifestDigestValidationError) as exp:
                for chunk in stream:
                    pass
            assert str(exp.value) == "The content of retrieved blob digest does not match the requested digest."
