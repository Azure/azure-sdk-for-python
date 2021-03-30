# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import os

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
    ContainerRegistryUserCredential,
    TagProperties,
    ContentPermissions,
    RegistryArtifactProperties,
)


class ContainerRegistryTestClass(object):
    def create_registry_client(self, endpoint):
        return ContainerRegistryClient(
            endpoint=endpoint,
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"],
            ),
        )

    def create_repository_client(self, endpoint, name):
        return ContainerRepositoryClient(
            endpoint=endpoint,
            repository=name,
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"],
            ),
        )

    def assert_content_permission(self, content_perm, content_perm2):
        assert isinstance(content_perm, ContentPermissions)
        assert isinstance(content_perm2, ContentPermissions)
        assert content_perm.can_delete == content_perm.can_delete
        assert content_perm.can_list == content_perm.can_list
        assert content_perm.can_read == content_perm.can_read
        assert content_perm.can_write == content_perm.can_write

    def assert_tag(
        self,
        tag,
        created_on=None,
        digest=None,
        last_updated_on=None,
        content_permission=None,
        name=None,
        registry=None,
        repository=None,
    ):
        assert isinstance(tag, TagProperties)
        assert isinstance(tag.content_permissions, ContentPermissions)
        assert isinstance(tag.created_on, datetime)
        assert isinstance(tag.last_updated_on, datetime)
        if content_permission:
            self.assert_content_permission(tag.content_permission, content_permission)
        if created_on:
            assert tag.created_on == created_on
        if last_updated_on:
            assert tag.last_updated_on == last_updated_on
        if name:
            assert tag.name == name
        if registry:
            assert tag.registry == registry
        if repository:
            assert tag.repository == repository

    def assert_registry_artifact(self, tag_or_digest, expected_tag_or_digest):
        assert isinstance(tag_or_digest, RegistryArtifactProperties)
        assert tag_or_digest == expected_tag_or_digest
