# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from typing import TYPE_CHECKING
from ._generated.models import ContentProperties

if TYPE_CHECKING:
    from ._generated.models import ManifestAttributesBase
    from ._generated.models import RepositoryProperties as GeneratedRepositoryProperties
    from ._generated.models import TagProperties as GeneratedTagProperties


class ContentPermissions(object):
    def __init__(self, **kwargs):
        self.can_delete = kwargs.get("can_delete")
        self.can_list = kwargs.get("can_list")
        self.can_read = kwargs.get("can_read")
        self.can_write = kwargs.get("can_write")

    @classmethod
    def _from_generated(cls, generated):
        # type: (ContentProperties) -> ContentPermissions
        return cls(
            can_delete=generated.can_delete,
            can_list=generated.can_list,
            can_read=generated.can_read,
            can_write=generated.can_write,
        )

    def _to_generated(self):
        # type: () -> ContentProperties
        return ContentProperties(
            can_delete=self.can_delete,
            can_list=self.can_list,
            can_read=self.can_read,
            can_write=self.can_write,
        )


class DeletedRepositoryResult(object):
    def __init__(self, **kwargs):
        self.deleted_registry_artifact_digests = kwargs.get("deleted_registry_artifact_digests", None)
        self.deleted_tags = kwargs.get("deleted_tags", None)

    @classmethod
    def _from_generated(cls, gen):
        return cls(
            deleted_tags=gen.deleted_tags,
            deleted_registry_artifact_digests=gen.deleted_registry_artifact_digests,
        )


class RegistryArtifactProperties(object):
    def __init__(self, **kwargs):
        self.cpu_architecture = kwargs.get("cpu_architecture", None)
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.operating_system = kwargs.get("operating_system", None)
        self.references = kwargs.get("references", None)
        self.size = kwargs.get("size", None)
        self.tags = kwargs.get("tags", None)
        self.content_permissions = kwargs.get("content_permissions", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)

    @classmethod
    def _from_generated(cls, generated):
        # type: (ManifestAttributesBase) -> RegistryArtifactProperties
        return cls(
            cpu_architecture=generated.cpu_architecture,
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            operating_system=generated.operating_system,
            size=generated.size,
            tags=generated.tags,
            content_permissions=generated.writeable_properties,
        )


class RepositoryProperties(object):
    """Model for storing properties of a single repository

    :ivar created_on: Time the repository was created
    :vartype created_on: str
    :ivar last_updated_on: Time the repository was last updated
    :vartype last_updated_on: str
    :ivar modifiable_properties: Read/Write/Update/Delete permissions for the repository
    :vartype modifiable_properties: ContentPermissions
    :ivar name: Name of the repository
    :vartype name: str
    :ivar registry: Registry the repository belongs to
    :vartype registry: str
    :ivar digest: The digest of the repository
    :vartype digest: str
    :ivar tag_count: Number of tags associated with the repository
    :vartype tag_count: int
    :ivar manifest_count: Number of manifest in the repository
    :vartype manifest_count: int
    """

    def __init__(self, **kwargs):
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.name = kwargs.get("name", None)
        self.registry = kwargs.get("registry", None)
        self.manifest_count = kwargs.get("manifest_count", None)
        self.tag_count = kwargs.get("tag_count", None)
        self.content_permissions = kwargs.get("content_permissions", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedRepositoryProperties) -> RepositoryProperties
        return cls(
            created_on=generated.created_on,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            manifest_count=generated.registry_artifact_count,
            tag_count=generated.tag_count,
            content_permissions=generated.writeable_properties,
            registry=generated.additional_properties.get("registry", None),
        )


class RegistryArtifactOrderBy(str, Enum):

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagOrderBy(str, Enum):

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagProperties(object):
    """Model for storing properties of a single tag

    :ivar created_on: Time the tag was created
    :vartype created_on: datetime
    :ivar digest: Digest for the tag
    :vartype digest: str
    :ivar last_updated_on: Time the tag was last updated
    :vartype last_updated_on: datetime
    :ivar modifiable_properties: Read/Write/Update/Delete permissions for the tag
    :vartype modifiable_properties: ContentPermissions
    :ivar name: Name of the image the tag corresponds to
    :vartype name: str
    :ivar registry: Registry the tag belongs to
    :vartype registry: str
    :ivar repository: Repository the tag belongs to
    :vartype repository: str
    """

    def __init__(self, **kwargs):
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.content_permissions = kwargs.get("writeable_properties", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)
        self.name = kwargs.get("name", None)

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedTagProperties) -> TagProperties
        return cls(
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            writeable_properties=generated.writeable_properties,
        )
