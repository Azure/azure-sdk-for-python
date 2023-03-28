# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import pytest
import six

from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
    ArtifactManifestOrder,
    ArtifactTagProperties,
    ArtifactTagOrder,
)
from azure.containerregistry.aio import ContainerRegistryClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from azure.core.async_paging import AsyncItemPaged
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
    
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_set_audience(self, containerregistry_endpoint):
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority=authority)
        valid_audience = get_audience(authority)

        async with ContainerRegistryClient(
            endpoint=containerregistry_endpoint, credential=credential, audience=valid_audience
        ) as client:
            assert client._client._config.api_version == "2021-07-01"
            async for repo in client.list_repository_names():
                pass
        
        async with ContainerRegistryClient(endpoint=containerregistry_endpoint, credential=credential) as client:
            if valid_audience == get_audience(AzureAuthorityHosts.AZURE_PUBLIC_CLOUD):
                async for repo in client.list_repository_names():
                    pass

                invalid_audience = get_audience(AzureAuthorityHosts.AZURE_GOVERNMENT)
                invalid_client = ContainerRegistryClient(
                    endpoint=containerregistry_endpoint, credential=credential, audience=invalid_audience
                )
                with pytest.raises(ClientAuthenticationError):
                    async for repo in invalid_client.list_repository_names():
                        pass
            else:
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
