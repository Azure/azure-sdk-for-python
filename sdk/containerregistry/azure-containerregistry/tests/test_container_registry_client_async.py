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
from typing import Optional, AsyncIterator, Any, MutableMapping
from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
    ArtifactManifestOrder,
    ArtifactTagProperties,
    ArtifactTagOrder,
    ManifestDigestValidationError,
)
from azure.containerregistry.aio import ContainerRegistryClient
from azure.containerregistry._helpers import DOCKER_MANIFEST, OCI_IMAGE_MANIFEST, DEFAULT_CHUNK_SIZE
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError, HttpResponseError
from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import PipelineRequest
from azure.identity import AzureAuthorityHosts
from asynctestcase import AsyncContainerRegistryTestClass, get_authority, get_audience
from constants import HELLO_WORLD, ALPINE, BUSYBOX, DOES_NOT_EXIST
from preparer import acr_preparer
from devtools_testutils.aio import recorded_by_proxy_async


class TestContainerRegistryClientAsync(AsyncContainerRegistryTestClass):
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_repository_names(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
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
    @recorded_by_proxy_async
    async def test_list_repository_names_by_page(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
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
    @recorded_by_proxy_async
    async def test_delete_repository(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [repo])
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_repository(repo)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                await client.get_repository_properties(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_repository(DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_repository_properties(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = await client.get_repository_properties(ALPINE)
            assert isinstance(properties, RepositoryProperties)
            assert properties.name == ALPINE

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_repository_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = self.set_all_properties(RepositoryProperties(), False)
            received = await client.update_repository_properties(repo, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = await client.update_repository_properties(repo, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_repository_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            received = await client.update_repository_properties(
                repo, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = await client.update_repository_properties(
                repo, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            count = 0
            async for artifact in client.list_manifest_properties(BUSYBOX):
                assert isinstance(artifact, ArtifactManifestProperties)
                assert isinstance(artifact.created_on, datetime)
                assert isinstance(artifact.last_updated_on, datetime)
                assert artifact.repository_name == BUSYBOX
                assert artifact.fully_qualified_reference in self.create_fully_qualified_reference(containerregistry_endpoint, BUSYBOX, artifact.digest)
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            results_per_page = 2

            pages = client.list_manifest_properties(BUSYBOX, results_per_page=results_per_page)
            page_count = 0
            async for page in pages.by_page():
                reg_count = 0
                async for tag in page:
                    reg_count += 1
                assert reg_count <= results_per_page
                page_count += 1

            assert page_count >= 1

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            async for artifact in client.list_manifest_properties(
                BUSYBOX, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING
            ):
                if prev_last_updated_on:
                    assert artifact.last_updated_on < prev_last_updated_on
                prev_last_updated_on = artifact.last_updated_on
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            async for artifact in client.list_manifest_properties(
                BUSYBOX, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_ASCENDING
            ):
                if prev_last_updated_on:
                    assert artifact.last_updated_on > prev_last_updated_on
                prev_last_updated_on = artifact.last_updated_on
                count += 1

            assert count > 0

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_manifest_properties(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = await client.get_manifest_properties(ALPINE, "latest")
            assert isinstance(properties, ArtifactManifestProperties)
            assert properties.repository_name == ALPINE
            assert properties.fully_qualified_reference in self.create_fully_qualified_reference(containerregistry_endpoint, ALPINE, properties.digest)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            manifest = await client.get_manifest_properties(ALPINE, "latest")
            invalid_digest = manifest.digest[:-10] + u"a" * 10

            with pytest.raises(ResourceNotFoundError):
                await client.get_manifest_properties(ALPINE, invalid_digest)
            with pytest.raises(ResourceNotFoundError):
                await client.get_manifest_properties(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client: 
            properties = self.set_all_properties(ArtifactManifestProperties(), False)
            received = await client.update_manifest_properties(repo, tag, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = await client.update_manifest_properties(repo, tag, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_manifest_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            received = await client.update_manifest_properties(
                repo, tag, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = await client.update_manifest_properties(
                repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_tag_properties(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = await client.get_tag_properties(ALPINE, "latest")
            assert isinstance(properties, ArtifactTagProperties)
            assert properties.name == "latest"

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_tag_properties_does_not_exist(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            with pytest.raises(ResourceNotFoundError):
                await client.get_tag_properties(DOES_NOT_EXIST, DOES_NOT_EXIST)
            with pytest.raises(ResourceNotFoundError):
                await client.get_tag_properties(ALPINE, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = self.set_all_properties(ArtifactTagProperties(), False)
            received = await client.update_tag_properties(repo, tag, properties)
            self.assert_all_properties(received, False)

            properties = self.set_all_properties(properties, True)
            received = await client.update_tag_properties(repo, tag, properties)
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_tag_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            received = await client.update_tag_properties(
                repo, tag, can_delete=False, can_read=False, can_write=False, can_list=False
            )
            self.assert_all_properties(received, False)

            received = await client.update_tag_properties(
                repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
            )
            self.assert_all_properties(received, True)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        async with self.create_registry_client(containerregistry_endpoint) as client:
            count = 0
            async for tag in client.list_tag_properties(ALPINE):
                assert f"{ALPINE}:{tag.name}" in tags
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties_order_descending(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        async with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            async for tag in client.list_tag_properties(ALPINE, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING):
                assert f"{ALPINE}:{tag.name}" in tags
                if prev_last_updated_on:
                    assert tag.last_updated_on < prev_last_updated_on
                prev_last_updated_on = tag.last_updated_on
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties_order_ascending(self, containerregistry_endpoint):
        tags = [f"{ALPINE}:latest"]
        async with self.create_registry_client(containerregistry_endpoint) as client:
            prev_last_updated_on = None
            count = 0
            async for tag in client.list_tag_properties(ALPINE, order_by=ArtifactTagOrder.LAST_UPDATED_ON_ASCENDING):
                assert f"{ALPINE}:{tag.name}" in tags
                if prev_last_updated_on:
                    assert tag.last_updated_on > prev_last_updated_on
                prev_last_updated_on = tag.last_updated_on
                count += 1
            assert count == 1

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_tag(repo, tag)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                await client.get_tag_properties(repo, tag)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_tag(DOES_NOT_EXIST, DOES_NOT_EXIST)
            await client.delete_tag(ALPINE, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_manifest(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [f"{repo}:{tag}"])

        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_manifest(repo, tag)

            self.sleep(10)
            with pytest.raises(ResourceNotFoundError):
                await client.get_manifest_properties(repo, tag)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_manifest_does_not_exist(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            manifest = await client.get_manifest_properties(ALPINE, "latest")
            invalid_digest = manifest.digest[:-10] + u"a" * 10

            await client.delete_manifest(ALPINE, invalid_digest)
            with pytest.raises(ResourceNotFoundError):
                await client.delete_manifest(ALPINE, DOES_NOT_EXIST)
            with pytest.raises(ResourceNotFoundError):
                await client.delete_manifest(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_expiration_time_parsing(self, containerregistry_endpoint):
        from azure.containerregistry.aio._async_authentication_policy import ContainerRegistryChallengePolicy
        async with self.create_registry_client(containerregistry_endpoint) as client:
            async for repo in client.list_repository_names():
                pass

            for policy in client._client._client._pipeline._impl_policies:
                if isinstance(policy, ContainerRegistryChallengePolicy):
                    policy._exchange_client._expiration_time = 0
                    break

            count = 0
            async for repo in client.list_repository_names():
                count += 1

            assert count >= 1

    # Live only, the fake credential doesn't check auth scope the same way
    @pytest.mark.live_test_only
    @acr_preparer()
    async def test_construct_container_registry_client(self, **kwargs):
        containerregistry_endpoint = kwargs.pop("containerregistry_endpoint")
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority)
        
        async with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, credential=credential, audience="https://microsoft.com"
        ) as client:
            with pytest.raises(ClientAuthenticationError):
                properties = await client.get_repository_properties(HELLO_WORLD)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_misspell_property(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            properties = await client.get_repository_properties(ALPINE)
            
            with pytest.warns(DeprecationWarning):
                last_udpated_on = properties.last_udpated_on
            last_updated_on = properties.last_updated_on
            assert last_udpated_on == last_updated_on
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_json(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_json, media_type=DOCKER_MANIFEST)
            digest = await client.set_manifest(repo, manifest_json)
            
            response = await client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_json_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_json, tag=tag, media_type=DOCKER_MANIFEST)
                digest = await client.set_manifest(repo, manifest_json, tag=tag)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_stream(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream)
            
            response = await client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_stream_without_spaces(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest_without_spaces.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream)
            
            response = await client.get_manifest(repo, digest)
            assert response.media_type == OCI_IMAGE_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_stream_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)
            
            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, tag=tag)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_oci_manifest_stream_without_spaces_with_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = "v1"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", "manifest_without_spaces.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_oci_manifest_prerequisites(repo, client)
            
            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    await client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, tag=tag)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == OCI_IMAGE_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_stream(self, containerregistry_endpoint):
        repo = "library/hello-world"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_stream)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)

            response = await client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_stream_without_spaces(self, containerregistry_endpoint):
        repo = "library/hello-world"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest_without_spaces.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_stream)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, media_type=DOCKER_MANIFEST)

            response = await client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_stream_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_stream, tag=tag)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_stream_without_spaces_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        # Reading data from a no space file to make this test pass in playback as test proxy cannot handle spaces correctly
        # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest_without_spaces.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_stream, tag=tag)
                manifest_stream.seek(0)
                digest = await client.set_manifest(repo, manifest_stream, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_json(self, containerregistry_endpoint):
        repo = "library/hello-world"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_json)
                digest = await client.set_manifest(repo, manifest_json, media_type=DOCKER_MANIFEST)
            
            response = await client.get_manifest(repo, digest)
            assert response.media_type == DOCKER_MANIFEST

            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)
    
    # Live only, as test proxy now cannot handle spaces correctly
    # issue: https://github.com/Azure/azure-sdk-tools/issues/5968
    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_docker_manifest_json_with_tag(self, containerregistry_endpoint):
        repo = "library/hello-world"
        tag = "v1"
        path = os.path.join(self.get_test_directory(), "data", "docker_artifact", "manifest.json")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await self.upload_docker_manifest_prerequisites(repo, client)

            with open(path, "rb") as manifest_stream:
                manifest_json = json.loads(manifest_stream.read().decode())
                with pytest.raises(HttpResponseError):
                    # It fails as the default media type is oci image manifest media type
                    await client.set_manifest(repo, manifest_json, tag=tag)
                digest = await client.set_manifest(repo, manifest_json, tag=tag, media_type=DOCKER_MANIFEST)
            
            response = await client.get_manifest(repo, tag)
            assert response.media_type == DOCKER_MANIFEST

            tags = (await client.get_manifest_properties(repo, digest)).tags
            assert len(tags) == 1
            assert tags[0] == tag
            
            await client.delete_manifest(repo, digest)
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_upload_blob(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        blob = "654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed"
        path = os.path.join(self.get_test_directory(), "data", "oci_artifact", blob)

        async with self.create_registry_client(containerregistry_endpoint) as client:
            # Act
            with open(path, "rb") as data:
                digest, blob_size = await client.upload_blob(repo, data)

            # Assert
            blob_content = b""
            stream = await client.download_blob(repo, digest)
            async for chunk in stream:
                blob_content += chunk
            assert len(blob_content) == blob_size

            await client.delete_blob(repo, digest)
            await client.delete_repository(repo)

    @pytest.mark.live_test_only
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_upload_large_blob_in_chunk(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        async with self.create_registry_client(containerregistry_endpoint) as client:
            # Test blob upload and download in equal size chunks
            blob_size = DEFAULT_CHUNK_SIZE * 1024 # 4GB
            data = b'\x00' * int(blob_size)
            digest, size = await client.upload_blob(repo, BytesIO(data))
            assert size == blob_size

            stream = await client.download_blob(repo, digest)
            size = 0
            with open("text1.txt", "wb") as file:
                async for chunk in stream:
                    size += file.write(chunk)
            assert size == blob_size

            await client.delete_blob(repo, digest)

            # Test blob upload and download in unequal size chunks
            blob_size = DEFAULT_CHUNK_SIZE * 1024 + 20
            data = b'\x00' * int(blob_size)
            digest, size = await client.upload_blob(repo, BytesIO(data))
            assert size == blob_size

            stream = await client.download_blob(repo, digest)
            size = 0
            with open("text2.txt", "wb") as file:
                async for chunk in stream:
                    size += file.write(chunk)
            assert size == blob_size

            await client.delete_blob(repo, digest)

            # Cleanup
            await client.delete_repository(repo)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_blob_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        hash_value = hashlib.sha256(b"test").hexdigest()
        digest = f"sha256:{hash_value}"
        async with self.create_registry_client(containerregistry_endpoint) as client:
            await client.delete_blob(repo, digest)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_audience(self, containerregistry_endpoint):
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority=authority)

        async with ContainerRegistryClient(endpoint=containerregistry_endpoint, credential=credential) as client:
            async for repo in client.list_repository_names():
                pass

        valid_audience = get_audience(authority)
        async with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, credential=credential, audience=valid_audience
        ) as client:
            async for repo in client.list_repository_names():
                pass

        if valid_audience == get_audience(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD):
            invalid_audience = get_audience(AzureAuthorityHosts.AZURE_GOVERNMENT)
            async with ContainerRegistryClient(
                endpoint=containerregistry_endpoint, credential=credential, audience=invalid_audience
            ) as client:
                with pytest.raises(ClientAuthenticationError):
                    async for repo in client.list_repository_names():
                        pass

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tags_in_empty_repo(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            # cleanup tags in ALPINE repo
            async for tag in client.list_tag_properties(ALPINE):
                await client.delete_tag(ALPINE, tag.name)
            
            response = client.list_tag_properties(ALPINE)
            if response is not None:
                async for tag in response:
                    pass
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_manifests_in_empty_repo(self, containerregistry_endpoint):
        async with self.create_registry_client(containerregistry_endpoint) as client:
            # cleanup manifests in ALPINE repo
            async for tag in client.list_tag_properties(ALPINE):
                await client.delete_manifest(ALPINE, tag.name)

            response = client.list_manifest_properties(ALPINE)
            if response is not None:
                async for manifest in response:
                    pass


class MyMagicMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        return self


class TestContainerRegistryClientAsyncUnitTests:
    containerregistry_endpoint="https://fake_url.azurecr.io"
    
    def text(self, encoding: Optional[str] = None) -> str:
            return '{"hello": "world"}'

    @pytest.mark.asyncio
    async def test_manifest_digest_validation(self):
        JSON = MutableMapping[str, Any]
            
        async def send_in_set_manifest(request: PipelineRequest, **kwargs) -> MyMagicMock:
            content_digest = hashlib.sha256(b"hello world").hexdigest()
            return MyMagicMock(
                status_code=201,
                headers={"Docker-Content-Digest": content_digest},
                content_type="application/json; charset=utf-8",
                text=self.text
        )
        
        async def read() -> bytes:
            return b'{"hello": "world"}'
        
        def json() -> JSON:
            return {"hello": "world"}
        
        async def send_in_get_manifest(request: PipelineRequest, **kwargs) -> MyMagicMock:
            content_digest = hashlib.sha256(b"hello world").hexdigest()
            content_type = "application/vnd.oci.image.manifest.v1+json"
            return MyMagicMock(
                status_code=200,
                headers={"Docker-Content-Digest": content_digest, "Content-Type": content_type},
                read=read,
                json=json
        )
            
        async with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MyMagicMock(send=send_in_set_manifest)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                manifest = {"hello": "world"}
                await client.set_manifest("test-repo", manifest)
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."
            
        async with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MyMagicMock(send=send_in_get_manifest)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                digest = hashlib.sha256(b"hello world").hexdigest()
                await client.get_manifest("test-repo", f"sha256:{digest}")
            assert str(exp.value) == "The content of retrieved manifest digest does not match the requested digest."
                
            with pytest.raises(ManifestDigestValidationError) as exp:
                await client.get_manifest("test-repo", "test-tag")
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."

    @pytest.mark.asyncio
    async def test_blob_digest_validation(self):
        async def send_in_upload_blob(request: PipelineRequest, **kwargs) -> MyMagicMock:
            if request.method == "PUT":
                content_digest = hashlib.sha256(b"hello world").hexdigest()
                return MyMagicMock(
                    status_code=201,
                    headers={"Docker-Content-Digest": content_digest},
                    content_type="application/json; charset=utf-8",
                    text=self.text
                )
            else:
                return MyMagicMock(
                    status_code=202,
                    headers={"Location": "/v2/test-repo/blobs/uploads/fake_location"},
                    content_type="application/json; charset=utf-8",
                    text=self.text
                )
        
        async def iter_bytes() -> AsyncIterator[bytes]:
            yield b'{"hello": "world"}'
        
        async def send_in_download_blob(request: PipelineRequest, **kwargs) -> MyMagicMock:
            return MyMagicMock(
                status_code=206,
                headers={"Content-Range": "bytes 0-27/28", "Content-Length": "28"},
                content_type="application/octet-stream",
                text=self.text,
                iter_bytes=iter_bytes
            )
            
        async with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MyMagicMock(send=send_in_upload_blob)
        ) as client:
            with pytest.raises(ManifestDigestValidationError) as exp:
                await client.upload_blob("test-repo", BytesIO(b'{"hello": "world"}'))
            assert str(exp.value) == "The server-computed digest does not match the client-computed digest."
            
        async with ContainerRegistryClient(
            endpoint=self.containerregistry_endpoint, transport = MyMagicMock(send=send_in_download_blob)
        ) as client:
            digest = hashlib.sha256(b"hello world").hexdigest()
            stream = await client.download_blob("test-repo", f"sha256:{digest}")
            with pytest.raises(ManifestDigestValidationError) as exp:
                async for chunk in stream:
                    pass
            assert str(exp.value) == "The content of retrieved blob digest does not match the requested digest."
