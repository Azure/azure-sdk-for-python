# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from typing import TYPE_CHECKING, Dict, Any, List

from ._generated.models import (
    ArtifactTagProperties as GeneratedArtifactTagProperties,
    RepositoryProperties as GeneratedRepositoryProperties,
    RepositoryWriteableProperties,
    TagWriteableProperties,
    ManifestWriteableProperties,
)
from ._helpers import _host_only, _is_tag, _strip_alg

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.models import ManifestAttributesBase


class ArtifactManifestProperties(object):  # pylint: disable=too-many-instance-attributes
    """Represents properties of a registry artifact

    :ivar bool can_delete: Delete Permissions for an artifact
    :ivar bool can_write: Delete Permissions for an artifact
    :ivar bool can_read: Delete Permissions for an artifact
    :ivar bool can_list: Delete Permissions for an artifact
    :ivar architecture: CPU Architecture of an artifact
    :vartype architecture: ~azure.containerregistry.ArtifactArchitecture
    :ivar created_on: Time and date an artifact was created
    :vartype created_on: ~datetime.datetime
    :ivar str digest: Digest for the artifact
    :ivar last_updated_on: Time and date an artifact was last updated
    :vartype last_updated_on: datetime.datetime
    :ivar operating_system: Operating system for the artifact
    :vartype operating_system: ~azure.containerregistry.ArtifactOperatingSystem
    :ivar str repository_name: Repository name the artifact belongs to
    :ivar str size: Size of the artifact
    :ivar List[str] tags: Tags associated with a registry artifact
    """

    def __init__(self, **kwargs):
        self._architecture = kwargs.get("cpu_architecture", None)
        if self._architecture is not None:
            self._architecture = ArtifactArchitecture(self._architecture)
        self._created_on = kwargs.get("created_on", None)
        self._digest = kwargs.get("digest", None)
        self._last_updated_on = kwargs.get("last_updated_on", None)
        self._operating_system = kwargs.get("operating_system", None)
        if self._operating_system is not None:
            self._operating_system = ArtifactOperatingSystem(self._operating_system)
        self._repository_name = kwargs.get("repository_name", None)
        self._registry = kwargs.get("registry", None)
        self._size = kwargs.get("size", None)
        self._tags = kwargs.get("tags", None)
        self.can_delete = kwargs.get("can_delete")
        self.can_read = kwargs.get("can_read")
        self.can_list = kwargs.get("can_list")
        self.can_write = kwargs.get("can_write")

    @classmethod
    def _from_generated(cls, generated, **kwargs):
        # type: (ManifestAttributesBase, Dict[str, Any]) -> ArtifactManifestProperties
        return cls(
            cpu_architecture=generated.architecture,
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            operating_system=generated.operating_system,
            size=generated.size,
            tags=generated.tags,
            can_delete=generated.can_delete,
            can_read=generated.can_read,
            can_write=generated.can_write,
            can_list=generated.can_list,
            repository_name=kwargs.get("repository_name", None),
            registry=kwargs.get("registry", None),
        )

    def _to_generated(self):
        # type: () -> ManifestWriteableProperties
        return ManifestWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def architecture(self):
        # type: () -> ArtifactArchitecture
        return self._architecture

    @property
    def created_on(self):
        # type: () -> datetime
        return self._created_on

    @property
    def digest(self):
        # type: () -> str
        return self._digest

    @property
    def last_updated_on(self):
        # type: () -> datetime
        return self._last_updated_on

    @property
    def operating_system(self):
        # type: () -> ArtifactOperatingSystem
        return self._operating_system

    @property
    def repository_name(self):
        # type: () -> str
        return self._repository_name

    @property
    def size(self):
        # type: () -> int
        return self._size

    @property
    def tags(self):
        # type: () -> List[str]
        return self._tags

    @property
    def fully_qualified_reference(self):
        # type: () -> str
        return "{}/{}{}{}".format(
            _host_only(self._registry),
            self._repository_name,
            ":" if _is_tag(self._digest) else "@",
            _strip_alg(self._digest)
        )

    def _to_generated(self):
        # type: () -> ManifestWriteableProperties
        return ManifestWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )


class RepositoryProperties(object):
    """Model for storing properties of a single repository

    :ivar bool can_delete: Delete Permissions for an artifact
    :ivar bool can_write: Delete Permissions for an artifact
    :ivar bool can_read: Delete Permissions for an artifact
    :ivar bool can_list: Delete Permissions for an artifact
    :ivar bool teleport_enabled: Teleport enabled for the repository
    :ivar created_on: Time the repository was created
    :vartype created_on: datetime.datetime
    :ivar last_updated_on: Time the repository was last updated
    :vartype last_updated_on: datetime.datetime
    :ivar int manifest_count: Number of manifest in the repository
    :ivar str name: Name of the repository
    :ivar int tag_count: Number of tags associated with the repository
    """

    def __init__(self, **kwargs):
        self._created_on = kwargs.get("created_on", None)
        self._last_updated_on = kwargs.get("last_updated_on", None)
        self._manifest_count = kwargs.get("manifest_count", None)
        self._name = kwargs.get("name", None)
        self._tag_count = kwargs.get("tag_count", None)
        self.can_delete = kwargs.get("can_delete")
        self.can_read = kwargs.get("can_read")
        self.can_list = kwargs.get("can_list")
        self.can_write = kwargs.get("can_write")
        self.teleport_enabled = kwargs.get("teleport_enabled")

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedRepositoryProperties) -> RepositoryProperties
        return cls(
            created_on=generated.created_on,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            manifest_count=generated.manifest_count,
            tag_count=generated.tag_count,
            can_delete=generated.can_delete,
            can_read=generated.can_read,
            can_write=generated.can_write,
            can_list=generated.can_list,
            teleport_enabled=generated.teleport_enabled,
        )

    def _to_generated(self):
        # type: () -> RepositoryWriteableProperties
        return RepositoryWriteableProperties(
            teleport_enabled=self.teleport_enabled,
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def created_on(self):
        # type: () -> datetime
        return self._created_on

    @property
    def last_udpated_on(self):
        # type: () -> datetime
        return self._last_updated_on

    @property
    def manifest_count(self):
        # type: () -> int
        return self._manifest_count

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def tag_count(self):
        # type: () -> int
        return self._tag_count


class ManifestOrder(str, Enum):
    """Enum for ordering registry artifacts"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagOrder(str, Enum):
    """Enum for ordering tags"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class ArtifactTagProperties(object):
    """Model for storing properties of a single tag

    :ivar bool can_delete: Delete Permissions for an artifact
    :ivar bool can_write: Delete Permissions for an artifact
    :ivar bool can_read: Delete Permissions for an artifact
    :ivar bool can_list: Delete Permissions for an artifact
    :ivar created_on: Time the tag was created
    :vartype created_on: datetime.datetime
    :ivar str digest: Digest for the tag
    :ivar last_updated_on: Time the tag was last updated
    :vartype last_updated_on: datetime.datetime
    :ivar str name: Name of the image the tag corresponds to
    :ivar str repository: Repository the tag belongs to
    """

    def __init__(self, **kwargs):
        self._created_on = kwargs.get("created_on", None)
        self._digest = kwargs.get("digest", None)
        self._last_updated_on = kwargs.get("last_updated_on", None)
        self._name = kwargs.get("name", None)
        self._repository_name = kwargs.get("repository_name", None)
        self.can_delete = kwargs.get("can_delete")
        self.can_read = kwargs.get("can_read")
        self.can_list = kwargs.get("can_list")
        self.can_write = kwargs.get("can_write")

    @classmethod
    def _from_generated(cls, generated, **kwargs):
        # type: (GeneratedArtifactTagProperties, Dict[str, Any]) -> ArtifactTagProperties
        return cls(
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            can_delete=generated.can_delete,
            can_read=generated.can_read,
            can_write=generated.can_write,
            can_list=generated.can_list,
            repository_name=kwargs.get("repository_name", None),
        )

    def _to_generated(self):
        # type: () -> TagWriteableProperties
        return TagWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def created_on(self):
        # type: () -> datetime
        return self._created_on

    @property
    def digest(self):
        # type: () -> str
        return self._digest

    @property
    def last_updated_on(self):
        # type: () -> datetime
        return self._last_updated_on

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def repository_name(self):
        # type: () -> str
        return self._repository_name


class ArtifactArchitecture(str, Enum):

    AMD64 = "amd64"
    ARM = "arm"
    ARM64 = "arm64"
    I386 = "386"
    MIPS = "mips"
    MIPS64 = "mips64"
    MIPS64LE = "mips64le"
    MIPSLE = "mipsle"
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
