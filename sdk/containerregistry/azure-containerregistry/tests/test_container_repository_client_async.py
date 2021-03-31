# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import pytest
import six
import subprocess
import time

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContentPermissions,
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from testcase import AcrBodyReplacer
from constants import TO_BE_DELETED


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
    containerregistry_resource_group="fake_rg",
)


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):

    def __init__(self, method_name):
        super(TestContainerRegistryClient, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AcrBodyReplacer())
        self.repository = "hello-world"

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_baseurl, containerregistry_resource_group):
        self._import_tag_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        tag = await client.get_tag_properties(TO_BE_DELETED)
        assert tag is not None

        await client.delete_tag(TO_BE_DELETED)
        self.sleep(10)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties(TO_BE_DELETED)

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        reg_client = self.create_registry_client(containerregistry_baseurl)
        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)
        await repo_client.delete()
        self.sleep(5)

        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    async def test_delete_repository_doesnt_exist(self, containerregistry_baseurl):
        DOES_NOT_EXIST = "does_not_exist"

        repo_client = self.create_repository_client(containerregistry_baseurl, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            await repo_client.delete()

    @acr_preparer()
    async def test_delete_registry_artifact(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)

        count = 0
        async for artifact in repo_client.list_registry_artifacts():
            if count == 0:
                await repo_client.delete_registry_artifact(artifact.digest)
            count += 1
        assert count > 0

        artifacts = []
        async for a in repo_client.list_registry_artifacts():
            artifacts.append(a)

        assert len(artifacts) > 0
        assert len(artifacts) == count - 1

    @acr_preparer()
    async def test_set_tag_properties(
        self, containerregistry_baseurl, containerregistry_resource_group
    ):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_repo_to_be_deleted(
            containerregistry_baseurl,
            resource_group=containerregistry_resource_group,
            tag=tag_identifier,
            repository=repository,
        )

        client = self.create_repository_client(containerregistry_baseurl, repository)

        tag_props = await client.get_tag_properties(tag_identifier)
        permissions = tag_props.content_permissions

        await client.set_tag_properties(tag_identifier, ContentPermissions(
            can_delete=False, can_list=False, can_read=False, can_write=False,
        ))
        self.sleep(10)

        received = await client.get_tag_properties(tag_identifier)

        assert received.content_permissions.can_write == False
        assert received.content_permissions.can_read == False
        assert received.content_permissions.can_list == False
        assert received.content_permissions.can_delete == False

    @acr_preparer()
    async def test_set_manifest_properties(
        self, containerregistry_baseurl, containerregistry_resource_group
    ):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_repo_to_be_deleted(
            containerregistry_baseurl,
            resource_group=containerregistry_resource_group,
            tag=tag_identifier,
            repository=repository,
        )

        client = self.create_repository_client(containerregistry_baseurl, repository)

        async for artifact in client.list_registry_artifacts():
            permissions = artifact.content_permissions

            await client.set_manifest_properties(artifact.digest, ContentPermissions(
                can_delete=False, can_list=False, can_read=False, can_write=False,
            ))
            self.sleep(10)

            received_permissions = await client.get_registry_artifact_properties(artifact.digest)

            assert received_permissions.content_permissions.can_delete == False
            assert received_permissions.content_permissions.can_read == False
            assert received_permissions.content_permissions.can_list == False
            assert received_permissions.content_permissions.can_write == False

            break