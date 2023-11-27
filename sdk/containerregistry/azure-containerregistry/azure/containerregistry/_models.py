# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import warnings
from datetime import datetime
from enum import Enum
from typing import Any, List, Mapping, Optional, Union, cast

from azure.core import CaseInsensitiveEnumMeta
from ._generated.models import (
    ContainerRepositoryProperties as GeneratedRepositoryProperties,
    RepositoryWriteableProperties,
    TagWriteableProperties,
    TagAttributesBase,
    ManifestWriteableProperties,
    ManifestAttributesBase,
)
from ._helpers import _host_only, _is_tag, _strip_alg


class ArtifactArchitecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


class ArtifactOperatingSystem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


class ArtifactManifestProperties:  # pylint: disable=too-many-instance-attributes
    """Represents properties of a registry artifact."""

    can_delete: Optional[bool]
    """Delete Permissions for an artifact."""
    can_read: Optional[bool]
    """Read Permissions for an artifact."""
    can_list: Optional[bool]
    """List Permissions for an artifact."""
    can_write: Optional[bool]
    """Write Permissions for an artifact."""

    def __init__(self, **kwargs: Any) -> None:
        self._architecture = kwargs.get("cpu_architecture", None)
        try:
            self._architecture = ArtifactArchitecture(self._architecture)
        except ValueError:
            pass
        self._created_on = kwargs.get("created_on", None)
        self._digest = kwargs.get("digest", None)
        self._last_updated_on = kwargs.get("last_updated_on", None)
        self._operating_system = kwargs.get("operating_system", None)
        try:
            self._operating_system = ArtifactOperatingSystem(self._operating_system)
        except ValueError:
            pass
        self._repository_name = kwargs.get("repository_name", None)
        self._registry = kwargs.get("registry", None)
        self._size_in_bytes = kwargs.get("size_in_bytes", None)
        self._tags = kwargs.get("tags", None)
        self.can_delete = kwargs.get("can_delete")
        self.can_read = kwargs.get("can_read")
        self.can_list = kwargs.get("can_list")
        self.can_write = kwargs.get("can_write")

    @classmethod
    def _from_generated(cls, generated: ManifestAttributesBase, **kwargs) -> "ArtifactManifestProperties":
        return cls(
            cpu_architecture=generated.architecture,
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            operating_system=generated.operating_system,
            size_in_bytes=generated.size,
            tags=generated.tags,
            can_delete=None if generated.changeable_attributes is None else generated.changeable_attributes.can_delete,
            can_read=None if generated.changeable_attributes is None else generated.changeable_attributes.can_read,
            can_write=None if generated.changeable_attributes is None else generated.changeable_attributes.can_write,
            can_list=None if generated.changeable_attributes is None else generated.changeable_attributes.can_list,
            repository_name=kwargs.get("repository_name"),
            registry=kwargs.get("registry"),
        )

    def _to_generated(self) -> ManifestWriteableProperties:
        return ManifestWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def architecture(self) -> Optional[Union[ArtifactArchitecture, str]]:
        """CPU Architecture of an artifact.

        :rtype: ~azure.containerregistry.ArtifactArchitecture or str or None
        """
        return self._architecture

    @property
    def created_on(self) -> datetime:
        """Time and date an artifact was created.

        :rtype: ~datetime.datetime
        """
        return self._created_on

    @property
    def digest(self) -> str:
        """Digest for the artifact.

        :rtype: str
        """
        return self._digest

    @property
    def last_updated_on(self) -> datetime:
        """Time and date an artifact was last updated.

        :rtype: ~datetime.datetime
        """
        return self._last_updated_on

    @property
    def operating_system(self) -> Optional[Union[ArtifactOperatingSystem, str]]:
        """Operating system for the artifact.

        :rtype: ~azure.containerregistry.ArtifactOperatingSystem or str or None
        """
        return self._operating_system

    @property
    def repository_name(self) -> str:
        """Repository name the artifact belongs to.

        :rtype: str
        """
        return self._repository_name

    @property
    def size_in_bytes(self) -> Optional[int]:
        """Size of the artifact.

        :rtype: int or None
        """
        return self._size_in_bytes

    @property
    def tags(self) -> Optional[List[str]]:
        """Tags associated with a registry artifact.

        :rtype: list[str] or None
        """
        return self._tags

    @property
    def fully_qualified_reference(self) -> str:
        """The fully qualified name of this artifact.

        :rtype: str
        """
        return f"{_host_only(self._registry)}/{self._repository_name}{':' if _is_tag(self._digest) else '@'}{_strip_alg(self._digest)}"  # pylint: disable=line-too-long


class RepositoryProperties:
    """Represents properties of a single repository."""

    can_delete: Optional[bool]
    """Delete Permissions for a repository."""
    can_read: Optional[bool]
    """Read Permissions for a repository."""
    can_list: Optional[bool]
    """List Permissions for a repository."""
    can_write: Optional[bool]
    """Write Permissions for a repository."""

    def __init__(self, **kwargs: Any) -> None:
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
    def _from_generated(cls, generated: GeneratedRepositoryProperties) -> "RepositoryProperties":
        return cls(
            created_on=generated.created_on,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            manifest_count=generated.manifest_count,
            tag_count=generated.tag_count,
            can_delete=generated.changeable_attributes.can_delete,
            can_read=generated.changeable_attributes.can_read,
            can_write=generated.changeable_attributes.can_write,
            can_list=generated.changeable_attributes.can_list,
        )

    def _to_generated(self) -> RepositoryWriteableProperties:
        return RepositoryWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    def __getattr__(self, name: str) -> Any:
        if name == "last_udpated_on":
            warnings.warn(
                "The property name with a typo called 'last_udpated_on' has been deprecated and will be retired \
                in future versions",
                DeprecationWarning,
            )
            return self.last_updated_on
        return self.__getattribute__(name)

    @property
    def created_on(self) -> datetime:
        """Time and date the repository was created.

        :rtype: ~datetime.datetime
        """
        return self._created_on

    @property
    def last_updated_on(self) -> datetime:
        """Time and date the repository was last updated.

        :rtype: ~datetime.datetime
        """
        return self._last_updated_on

    @property
    def manifest_count(self) -> int:
        """Number of manifests in the repository.

        :rtype: int
        """
        return self._manifest_count

    @property
    def name(self) -> str:
        """Name of the repository.

        :rtype: str
        """
        return self._name

    @property
    def tag_count(self) -> int:
        """Number of tags associated with the repository.

        :rtype: int
        """
        return self._tag_count


class ArtifactTagProperties:
    """Represents properties of a single tag."""

    can_delete: Optional[bool]
    """Delete Permissions for a tag."""
    can_read: Optional[bool]
    """Read Permissions for a tag."""
    can_list: Optional[bool]
    """List Permissions for a tag."""
    can_write: Optional[bool]
    """Write Permissions for a tag."""

    def __init__(self, **kwargs: Any) -> None:
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
    def _from_generated(cls, generated: TagAttributesBase, **kwargs) -> "ArtifactTagProperties":
        return cls(
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            can_delete=generated.changeable_attributes.can_delete,
            can_read=generated.changeable_attributes.can_read,
            can_write=generated.changeable_attributes.can_write,
            can_list=generated.changeable_attributes.can_list,
            repository_name=kwargs.get("repository_name"),
        )

    def _to_generated(self) -> TagWriteableProperties:
        return TagWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def created_on(self) -> datetime:
        """Time and date the tag was created.

        :rtype: ~datetime.datetime
        """
        return self._created_on

    @property
    def digest(self) -> str:
        """Digest for the tag.

        :rtype: str
        """
        return self._digest

    @property
    def last_updated_on(self) -> datetime:
        """Time and date the tag was last updated.

        :rtype: ~datetime.datetime
        """
        return self._last_updated_on

    @property
    def name(self) -> str:
        """Name of the tag.

        :rtype: str
        """
        return self._name

    @property
    def repository_name(self) -> str:
        """Repository name the tag belongs to.

        :rtype: str
        """
        return self._repository_name


class GetManifestResult:
    """The get manifest result."""

    manifest: Mapping[str, Any]
    """The manifest JSON."""
    media_type: str
    """The manifest's media type."""
    digest: str
    """The manifest's digest, calculated by the registry."""

    def __init__(self, **kwargs: Any) -> None:
        self.manifest = cast(Mapping[str, Any], kwargs.get("manifest"))
        self.media_type = str(kwargs.get("media_type"))
        self.digest = str(kwargs.get("digest"))


class DigestValidationError(ValueError):
    """Thrown when a manifest digest validation fails."""

    message: str
    """Message for caller describing the reason for the failure."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
