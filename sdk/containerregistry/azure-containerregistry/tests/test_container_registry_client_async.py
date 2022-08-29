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

from asynctestcase import AsyncContainerRegistryTestClass, get_authority
from constants import TO_BE_DELETED, HELLO_WORLD, ALPINE, BUSYBOX, DOES_NOT_EXIST
from preparer import acr_preparer
from devtools_testutils.aio import recorded_by_proxy_async


class TestContainerRegistryClientAsync(AsyncContainerRegistryTestClass):
    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_repository_names(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

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
        client = self.create_registry_client(containerregistry_endpoint)
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
    async def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_image(containerregistry_endpoint, HELLO_WORLD, [TO_BE_DELETED])
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_repository(TO_BE_DELETED)

        async for repo in client.list_repository_names():
            if repo == TO_BE_DELETED:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_repository("not_real_repo")

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_repository_properties(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_repository_properties(ALPINE)
        assert isinstance(properties, RepositoryProperties)
        assert properties.name == ALPINE

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_properties(self, containerregistry_endpoint):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repository, tag_identifier)])
        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_repository_properties(repository)

        properties.can_delete = False
        properties.can_read = False
        properties.can_list = False
        properties.can_write = False

        new_properties = await client.update_repository_properties(repository, properties)

        assert properties.can_delete == new_properties.can_delete
        assert properties.can_read == new_properties.can_read
        assert properties.can_list == new_properties.can_list
        assert properties.can_write == new_properties.can_write

        new_properties.can_delete = True
        new_properties.can_read = True
        new_properties.can_list = True
        new_properties.can_write = True

        new_properties = await client.update_repository_properties(repository, new_properties)

        assert new_properties.can_delete == True
        assert new_properties.can_read == True
        assert new_properties.can_list == True
        assert new_properties.can_write == True

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_repository_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_repository_properties(repo)
        properties = self.set_all_properties(properties, True)
        received = await client.update_repository_properties(repo, properties)
        self.assert_all_properties(properties, True)

        received = await client.update_repository_properties(repo, can_delete=False)
        assert received.can_delete == False
        assert received.can_list == True
        assert received.can_read == True
        assert received.can_write == True

        received = await client.update_repository_properties(repo, can_read=False)
        assert received.can_delete == False
        assert received.can_list == True
        assert received.can_read == False
        assert received.can_write == True

        received = await client.update_repository_properties(repo, can_write=False)
        assert received.can_delete == False
        assert received.can_list == True
        assert received.can_read == False
        assert received.can_write == False

        received = await client.update_repository_properties(repo, can_list=False)
        assert received.can_delete == False
        assert received.can_list == False
        assert received.can_read == False
        assert received.can_write == False

        received = await client.update_repository_properties(
            repo,
            can_delete=True,
            can_read=True,
            can_write=True,
            can_list=True,
        )

        self.assert_all_properties(received, True)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

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
        client = self.create_registry_client(containerregistry_endpoint)
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
        client = self.create_registry_client(containerregistry_endpoint)

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

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_manifest_properties(BUSYBOX, order_by="timedesc"):
            if prev_last_updated_on:
                assert artifact.last_updated_on < prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

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

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_manifest_properties(BUSYBOX, order_by="timeasc"):
            if prev_last_updated_on:
                assert artifact.last_updated_on > prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_manifest_properties(repo, tag)

        assert isinstance(properties, ArtifactManifestProperties)
        assert properties.repository_name == repo
        assert properties.fully_qualified_reference in self.create_fully_qualified_reference(containerregistry_endpoint, repo, properties.digest)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            properties = await client.get_manifest_properties("DOESNOTEXIST", "DOESNOTEXIST")

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_manifest_properties(repo, tag)
        properties.can_delete = False
        properties.can_read = False
        properties.can_write = False
        properties.can_list = False

        received = await client.update_manifest_properties(repo, tag, properties)

        assert received.can_delete == properties.can_delete
        assert received.can_read == properties.can_read
        assert received.can_write == properties.can_write
        assert received.can_list == properties.can_list

        properties.can_delete = True
        properties.can_read = True
        properties.can_write = True
        properties.can_list = True

        received = await client.update_manifest_properties(repo, tag, properties)

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_manifest_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_manifest_properties(repo, tag)
        received = await client.update_manifest_properties(repo, tag, can_delete=False)
        assert received.can_delete == False

        received = await client.update_manifest_properties(repo, tag, can_read=False)
        assert received.can_read == False

        received = await client.update_manifest_properties(repo, tag, can_write=False)
        assert received.can_write == False

        received = await client.update_manifest_properties(repo, tag, can_list=False)
        assert received.can_list == False

        received = await client.update_manifest_properties(
            repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
        )

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_tag_properties(repo, tag)

        assert isinstance(properties, ArtifactTagProperties)
        assert properties.name == tag

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_tag_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties("Nonexistent", "Nonexistent")

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_tag_properties(repo, tag)
        properties.can_delete = False
        properties.can_read = False
        properties.can_write = False
        properties.can_list = False
        received = await client.update_tag_properties(repo, tag, properties)

        assert received.can_delete == properties.can_delete
        assert received.can_read == properties.can_read
        assert received.can_write == properties.can_write
        assert received.can_list == properties.can_list

        properties.can_delete = True
        properties.can_read = True
        properties.can_write = True
        properties.can_list = True

        received = await client.update_tag_properties(repo, tag, properties)

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_update_tag_properties_kwargs(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_tag_properties(repo, tag)
        received = await client.update_tag_properties(repo, tag, can_delete=False)
        assert received.can_delete == False

        received = await client.update_tag_properties(repo, tag, can_read=False)
        assert received.can_read == False

        received = await client.update_tag_properties(repo, tag, can_write=False)
        assert received.can_write == False

        received = await client.update_tag_properties(repo, tag, can_list=False)
        assert received.can_list == False

        received = await client.update_tag_properties(
            repo, tag, can_delete=True, can_read=True, can_write=True, can_list=True
        )

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(containerregistry_endpoint, HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        count = 0
        async for tag in client.list_tag_properties(repo):
            assert "{}:{}".format(repo, tag.name) in tags
            count += 1
        assert count == 4

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties_order_descending(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(containerregistry_endpoint, HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tag_properties(repo, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING):
            assert "{}:{}".format(repo, tag.name) in tags
            if prev_last_updated_on:
                assert tag.last_updated_on < prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1
        assert count == 4

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tag_properties(repo, order_by="timedesc"):
            assert "{}:{}".format(repo, tag.name) in tags
            if prev_last_updated_on:
                assert tag.last_updated_on < prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1
        assert count == 4

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_list_tag_properties_order_ascending(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(containerregistry_endpoint, HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tag_properties(repo, order_by=ArtifactTagOrder.LAST_UPDATED_ON_ASCENDING):
            assert "{}:{}".format(repo, tag.name) in tags
            if prev_last_updated_on:
                assert tag.last_updated_on > prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1
        assert count == 4

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tag_properties(repo, order_by="timeasc"):
            assert "{}:{}".format(repo, tag.name) in tags
            if prev_last_updated_on:
                assert tag.last_updated_on > prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1
        assert count == 4

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(containerregistry_endpoint, HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_tag(repo, tag + str(0))

        count = 0
        async for tag in client.list_tag_properties(repo):
            assert "{}:{}".format(repo, tag.name) in tags[1:]
            count += 1
        assert count == 3

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_tag(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_manifest(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)
        await client.delete_manifest(repo, tag)

        self.sleep(10)
        with pytest.raises(ResourceNotFoundError):
            await client.get_manifest_properties(repo, tag)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_delete_manifest_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(containerregistry_endpoint, HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        manifest = await client.get_manifest_properties(repo, tag)

        digest = manifest.digest

        digest = digest[:-10] + u"a" * 10

        await client.delete_manifest(repo, digest)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_expiration_time_parsing(self, containerregistry_endpoint):
        from azure.containerregistry.aio._async_authentication_policy import ContainerRegistryChallengePolicy
        client = self.create_registry_client(containerregistry_endpoint)

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
    @recorded_by_proxy_async
    async def test_construct_container_registry_client(self, containerregistry_endpoint):
        authority = get_authority(containerregistry_endpoint)
        credential = self.get_credential(authority)
        
        client = ContainerRegistryClient(endpoint=containerregistry_endpoint, credential=credential, audience="https://microsoft.com")
        with pytest.raises(ClientAuthenticationError):
            properties = await client.get_repository_properties(HELLO_WORLD)       
        with pytest.raises(TypeError):
            client = ContainerRegistryClient(endpoint=containerregistry_endpoint, credential=credential)

    @acr_preparer()
    @recorded_by_proxy_async
    async def test_get_misspell_property(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)
        properties = await client.get_repository_properties(ALPINE)
        
        with pytest.warns(DeprecationWarning):
            last_udpated_on = properties.last_udpated_on
        last_updated_on = properties.last_updated_on
        assert last_udpated_on == last_updated_on


def test_set_api_version():
    containerregistry_endpoint="https://fake_url.azurecr.io"
    
    client = ContainerRegistryClient(endpoint=containerregistry_endpoint, audience="https://microsoft.com")
    assert client._client._config.api_version == "2021-07-01"
    
    client = ContainerRegistryClient(endpoint=containerregistry_endpoint, audience="https://microsoft.com", api_version = "2019-08-15-preview")
    assert client._client._config.api_version == "2019-08-15-preview"
    
    with pytest.raises(ValueError):
        client = ContainerRegistryClient(endpoint=containerregistry_endpoint, audience="https://microsoft.com", api_version = "2019-08-15")
