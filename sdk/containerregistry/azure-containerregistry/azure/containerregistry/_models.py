# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from typing import TYPE_CHECKING

from ._generated.models import ContentProperties
from ._generated.models import RepositoryProperties as GeneratedRepositoryProperties

if TYPE_CHECKING:
    from ._generated.models import ManifestAttributesBase
    from ._generated.models import ArtifactTagProperties as GeneratedTagProperties


class ContentPermissions(object):
    """Permissions of an artifact or tag

    :ivar bool can_delete: Ability to delete an artifact or tag
    :ivar bool can_list: Ability to list an artifact or tag
    :ivar bool can_read: Ability to read an artifact or tag
    :ivar bool can_write: Ability to write an artifact or tag
    """

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
    """Represents the digests and tags deleted when a repository is deleted

    :ivar List[str] deleted_registry_artifact_digests: Registry artifact digests that were deleted
    :ivar List[str] deleted_tags: Tags that were deleted
    """

    def __init__(self, **kwargs):
        self.deleted_registry_artifact_digests = kwargs.get("deleted_registry_artifact_digests", None)
        self.deleted_tags = kwargs.get("deleted_tags", None)

    @classmethod
    def _from_generated(cls, gen):
        return cls(
            deleted_tags=gen.deleted_tags,
            deleted_registry_artifact_digests=gen.deleted_manifests,
        )


class ArtifactManifestProperties(object):
    """Represents properties of a registry artifact

    :ivar architecture: CPU Architecture of an artifact
    :vartype architecture: :class:`azure.containerregistry.ArtifactArchitecture`
    :ivar created_on: Time and date an artifact was created
    :vartype created_on: :class:`~datetime.datetime`
    :ivar str digest: Digest for the artifact
    :ivar last_updated_on: Time and date an artifact was last updated
    :vartype last_updated_on: :class:`~datetime.datetime`
    :ivar operating_system: Operating system for the artifact
    :vartype operating_system: :class:`azure.containerregistry.ArtifactOperatingSystem`
    :ivar List[str] references: References for the artifact
    :ivar str size: Size of the artifact
    :ivar List[str] tags: Tags associated with a registry artifact
    :ivar content_permissions: Permissions for an artifact
    :vartype content_permissions: :class:`~azure.containerregistry.ContentPermissions`
    """

    def __init__(self, **kwargs):
        self.architecture = _map_architecture(kwargs.get("cpu_architecture", None))
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.operating_system = _map_operating_system(kwargs.get("operating_system", None))
        self.references = kwargs.get("references", None)
        self.size = kwargs.get("size", None)
        self.tags = kwargs.get("tags", None)
        self.content_permissions = kwargs.get("content_permissions", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)

    @classmethod
    def _from_generated(cls, generated):
        # type: (ManifestAttributesBase) -> ArtifactManifestProperties
        return cls(
            cpu_architecture=generated.architecture,
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

    :ivar content_permissions: Read/Write/List/Delete permissions for the repository
    :vartype content_permissions: :class:`~azure.containerregistry.ContentPermissions`
    :ivar created_on: Time the repository was created
    :vartype created_on: :class:`datetime.datetime`
    :ivar last_updated_on: Time the repository was last updated
    :vartype last_updated_on: :class:`datetime.datetime`
    :ivar int manifest_count: Number of manifest in the repository
    :ivar str name: Name of the repository
    :ivar str registry: Registry the repository belongs to
    :ivar int tag_count: Number of tags associated with the repository
    """

    def __init__(self, **kwargs):
        self.content_permissions = kwargs.get("content_permissions", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.manifest_count = kwargs.get("manifest_count", None)
        self.name = kwargs.get("name", None)
        self.registry = kwargs.get("registry", None)
        self.tag_count = kwargs.get("tag_count", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedRepositoryProperties) -> RepositoryProperties
        return cls(
            created_on=generated.created_on,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            manifest_count=generated.manifest_count,
            tag_count=generated.tag_count,
            content_permissions=generated.writeable_properties,
            registry=generated.additional_properties.get("registry", None),
        )

    def _to_generated(self):
        # type: () -> GeneratedRepositoryProperties
        return GeneratedRepositoryProperties(
            name=self.name,
            created_on=self.created_on,
            last_updated_on=self.last_updated_on,
            manifest_count=self.manifest_count,
            tag_count=self.tag_count,
            writeable_properties=self.content_permissions._to_generated(),  # pylint: disable=protected-access
        )


class RegistryArtifactOrderBy(str, Enum):
    """Enum for ordering registry artifacts"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagOrderBy(str, Enum):
    """Enum for ordering tags"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagProperties(object):
    """Model for storing properties of a single tag

    :ivar content_permissions: Read/Write/List/Delete permissions for the tag
    :vartype content_permissions: :class:`~azure.containerregistry.ContentPermissions`
    :ivar created_on: Time the tag was created
    :vartype created_on: :class:`datetime.datetime`
    :ivar str digest: Digest for the tag
    :ivar last_updated_on: Time the tag was last updated
    :vartype last_updated_on: :class:`datetime.datetime`
    :ivar str name: Name of the image the tag corresponds to
    :ivar str registry: Registry the tag belongs to
    """

    def __init__(self, **kwargs):
        self.content_permissions = kwargs.get("writeable_properties", None)
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.name = kwargs.get("name", None)
        if self.content_permissions:
            self.content_permissions = ContentPermissions._from_generated(self.content_permissions)

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


def _map_architecture(arch):
    # type: (str) -> ArtifactArchitecture
    if arch is None:
        return None
    m = {
        "amd64": ArtifactArchitecture.AMD64,
        "arm": ArtifactArchitecture.ARM,
        "arm64": ArtifactArchitecture.ARM64,
        "386": ArtifactArchitecture.I386,
        "mips": ArtifactArchitecture.MIPS,
        "mips64": ArtifactArchitecture.MIPS64,
        "mips64le": ArtifactArchitecture.MIPS64LE,
        "mips64le": ArtifactArchitecture.MIPSLE,
        "ppc64": ArtifactArchitecture.PPC64,
        "ppc64le": ArtifactArchitecture.PPC64LE,
        "riscv64": ArtifactArchitecture.RISCV64,
        "s390x": ArtifactArchitecture.S390X,
        "wasm": ArtifactArchitecture.WASM,
    }
    return m[arch]


def _map_operating_system(os):
    # type: (str) -> ArtifactOperatingSystem
    if os is None:
        return None
    m = {
        "aix": ArtifactOperatingSystem.AIX,
        "android": ArtifactOperatingSystem.ANDROID,
        "darwin": ArtifactOperatingSystem.DARWIN,
        "dragonfly": ArtifactOperatingSystem.DRAGONFLY,
        "freebsd": ArtifactOperatingSystem.FREEBSD,
        "illumos": ArtifactOperatingSystem.ILLUMOS,
        "ios": ArtifactOperatingSystem.IOS,
        "js": ArtifactOperatingSystem.JS,
        "linux": ArtifactOperatingSystem.LINUX,
        "netbsd": ArtifactOperatingSystem.NETBSD,
        "openbsd": ArtifactOperatingSystem.OPENBSD,
        "plan9": ArtifactOperatingSystem.PLAN9,
        "solaris": ArtifactOperatingSystem.SOLARIS,
        "windows": ArtifactOperatingSystem.WINDOWS,
    }
    return m[os]

class ArtifactArchitecture(str, Enum):

    AMD64 = "amd64"
    ARM = "arm"
    ARM64 = "arm64"
    I386 = "i386"
    MIPS = "mips"
    MIPS64 = "mips64"
    MIPS64LE = "mips64le"
    MIPSLE = "mips64le"
    PPC64 = "ppc64"
    PPC64LE = "ppc64le"
    RISCV64 = "riscv64"
    S390X = "s390x"
    WASM = "wasm"


class ArtifactOperatingSystem(str, Enum):

    AIX = "aix"
    ANDROID = "android"
    DARWIN = "darwin"
    DRAGONFLY = "dragonfly"
    FREEBSD = "freebsd"
    ILLUMOS = "illumos"
    IOS = "ios"
    JS = "js"
    LINUX = "linux"
    NETBSD = "netbsd"
    OPENBSD = "openbsd"
    PLAN9 = "plan9"
    SOLARIS = "solaris"
    WINDOWS = "windows"
