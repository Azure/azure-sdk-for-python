# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import warnings
from enum import Enum
from typing import TYPE_CHECKING, Dict, Any, List

from ._generated.models import (
    ArtifactTagProperties as GeneratedArtifactTagProperties,
    ContainerRepositoryProperties as GeneratedRepositoryProperties,
    RepositoryWriteableProperties,
    TagWriteableProperties,
    ManifestWriteableProperties,
)
from ._helpers import _host_only, _is_tag, _strip_alg

if TYPE_CHECKING:
    from typing import IO
    from datetime import datetime
    from ._generated.models import ManifestAttributesBase, OCIManifest


class ArtifactManifestProperties(object):  # pylint: disable=too-many-instance-attributes
    """Represents properties of a registry artifact.

    :ivar bool can_delete: Delete Permissions for an artifact.
    :ivar bool can_write: Write Permissions for an artifact.
    :ivar bool can_read: Read Permissions for an artifact.
    :ivar bool can_list: List Permissions for an artifact.
    :ivar architecture: CPU Architecture of an artifact.
    :vartype architecture: ~azure.containerregistry.ArtifactArchitecture
    :ivar created_on: Time and date an artifact was created.
    :vartype created_on: ~datetime.datetime
    :ivar str digest: Digest for the artifact.
    :ivar last_updated_on: Time and date an artifact was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar operating_system: Operating system for the artifact.
    :vartype operating_system: ~azure.containerregistry.ArtifactOperatingSystem
    :ivar str repository_name: Repository name the artifact belongs to.
    :ivar str size_in_bytes: Size of the artifact.
    :ivar List[str] tags: Tags associated with a registry artifact.
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
        self._size_in_bytes = kwargs.get("size_in_bytes", None)
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
            size_in_bytes=generated.size,
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
    def size_in_bytes(self):
        # type: () -> int
        return self._size_in_bytes

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
    """Represents properties of a single repository.

    :ivar bool can_delete: Delete Permissions for a repository.
    :ivar bool can_write: Write Permissions for a repository.
    :ivar bool can_read: Read Permissions for a repository.
    :ivar bool can_list: List Permissions for a repository.
    :ivar created_on: Time the repository was created
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Time the repository was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar int manifest_count: Number of manifest in the repository.
    :ivar str name: Name of the repository.
    :ivar int tag_count: Number of tags associated with the repository.
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
        )

    def _to_generated(self):
        # type: () -> RepositoryWriteableProperties
        return RepositoryWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    def __getattr__(self, name):
        if name == "last_udpated_on":
            warnings.warn(
                "The property name with a typo called 'last_udpated_on' has been deprecated and will be retired in future versions", # pylint: disable=line-too-long
                DeprecationWarning)
            return self.last_updated_on
        return super().__getattr__(self, name) # pylint: disable=no-member

    @property
    def created_on(self):
        # type: () -> datetime
        return self._created_on

    @property
    def last_updated_on(self):
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


class ArtifactTagProperties(object):
    """Represents properties of a single tag

    :ivar bool can_delete: Delete Permissions for a tag.
    :ivar bool can_write: Write Permissions for a tag.
    :ivar bool can_read: Read Permissions for a tag.
    :ivar bool can_list: List Permissions for a tag.
    :ivar created_on: Time the tag was created.
    :vartype created_on: ~datetime.datetime
    :ivar str digest: Digest for the tag.
    :ivar last_updated_on: Time the tag was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar str name: Name of the image the tag corresponds to.
    :ivar str repository: Repository the tag belongs to.
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


class DownloadBlobResult(object):
    """The result from downloading a blob from the registry.

    :ivar data: The blob content.
    :vartype data: IO
    :ivar str digest: The blob's digest, calculated by the registry.
    """

    def __init__(self, **kwargs):
        self.data = kwargs.get("data")
        self.digest = kwargs.get("digest")


class DownloadManifestResult(object):
    """The result from downloading a manifest from the registry.

    :ivar manifest: The OCI manifest that was downloaded.
    :vartype manifest: ~azure.containerregistry.models.OCIManifest
    :ivar data: The manifest stream that was downloaded.
    :vartype data: IO
    :ivar str digest: The manifest's digest, calculated by the registry.
    """

    def __init__(self, **kwargs):
        self.manifest = kwargs.get("manifest")
        self.data = kwargs.get("data")
        self.digest = kwargs.get("digest")


class ArtifactArchitecture(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta

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


class ArtifactOperatingSystem(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta

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
