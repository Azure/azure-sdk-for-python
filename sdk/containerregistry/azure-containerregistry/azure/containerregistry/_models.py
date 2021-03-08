# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

from ._generated.models import (
    DeletedRepository,
)


class ContainerRegistryUserCredential(object):
    def __init__(self, username, password, **kwargs):
        # type: (str, str) -> None
        self.username = username
        self.password = password

    def update_password(self, password, **kwargs):
        # type: (str) -> None
        self.password = password

    def update_username(self, username, **kwargs):
        # type: (str) -> None
        self.username = username


class ContentPermissions(object):
    def __init__(self, **kwargs):
        self.delete = kwargs.get("delete")
        self.list = kwargs.get("list")
        self.read = kwargs.get("read")
        self.write = kwargs.get("write")


class DeletedRepositoryResult(DeletedRepository):
    def __init__(self, **kwargs):
        super(DeletedRepositoryResult, self).__init__(**kwargs)
        self.deleted_registry_artifact_digests = kwargs.get(
            "deleted_registry_artifact_digests", None
        )
        self.deleted_tags = kwargs.get("deleted_tags", None)
        pass


class RegistryArtifactProperties(object):
    def __init__(self, **kwargs):
        self.cpu_arch = kwargs.get("arch", None)
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated = kwargs.get("last_updated", None)
        self.manifest_properties = kwargs.get("manifest_properties", None)
        self.operating_system = kwargs.get("operating_system", None)
        self.registry = kwargs.get("registry", None)
        self.registry_artifacts = kwargs.get("registry_artifacts", None)
        self.repository = kwargs.get("repository", None)
        self.size = kwargs.get("size", None)
        self.tags = kwargs.get("tags", None)


class RepositoryProperties(object):
    def __init__(self, **kwargs):
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.modifiable_properties = kwargs.get("modifiable_properties", None)
        self.name = kwargs.get("name", None)
        self.registry = kwargs.get("registry", None)
        self.repository = kwargs.get("repository", None)


class RegistryArtifactOrderBy(int, Enum):

    LastUpdateTimeDescending = 0
    LastUpdateTimeAscending = 1


class TagOrderBy(int, Enum):

    LastUpdateTimeDescending = 0
    LastUpdateTimeAscending = 1
