# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import warnings
from datetime import datetime
from enum import Enum
from typing import List

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


class ArtifactManifestProperties(object):  # pylint: disable=too-many-instance-attributes
    """Represents properties of a registry artifact.

    :ivar bool can_delete: Delete Permissions for an artifact.
    :ivar bool can_write: Write Permissions for an artifact.
    :ivar bool can_read: Read Permissions for an artifact.
    :ivar bool can_list: List Permissions for an artifact.
    :ivar architecture: CPU Architecture of an artifact.
    :vartype architecture: Optional[~azure.containerregistry.ArtifactArchitecture]
    :ivar created_on: Time and date an artifact was created.
    :vartype created_on: Optional[~datetime.datetime]
    :ivar Optional[str] digest: Digest for the artifact.
    :ivar last_updated_on: Time and date an artifact was last updated.
    :vartype last_updated_on: Optional[~datetime.datetime]
    :ivar operating_system: Operating system for the artifact.
    :vartype operating_system: Optional[~azure.containerregistry.ArtifactOperatingSystem]
    :ivar Optional[str] repository_name: Repository name the artifact belongs to.
    :ivar Optional[int] size_in_bytes: Size of the artifact.
    :ivar Optional[List[str]] tags: Tags associated with a registry artifact.
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
            repository_name=kwargs.get("repository_name", None),
            registry=kwargs.get("registry", None),
        )

    def _to_generated(self) -> ManifestWriteableProperties:
        return ManifestWriteableProperties(
            can_delete=self.can_delete,
            can_read=self.can_read,
            can_write=self.can_write,
            can_list=self.can_list,
        )

    @property
    def architecture(self) -> ArtifactArchitecture:
        return self._architecture

    @property
    def created_on(self) -> datetime:
        return self._created_on

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def last_updated_on(self) -> datetime:
        return self._last_updated_on

    @property
    def operating_system(self) -> ArtifactOperatingSystem:
        return self._operating_system

    @property
    def repository_name(self) -> str:
        return self._repository_name

    @property
    def size_in_bytes(self) -> int:
        return self._size_in_bytes

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def fully_qualified_reference(self) -> str:
        return f"{_host_only(self._registry)}/{self._repository_name}{':' if _is_tag(self._digest) else '@'}{_strip_alg(self._digest)}" # pylint: disable=line-too-long


class RepositoryProperties(object):
    """Represents properties of a single repository.

    :ivar bool can_delete: Delete Permissions for a repository.
    :ivar bool can_write: Write Permissions for a repository.
    :ivar bool can_read: Read Permissions for a repository.
    :ivar bool can_list: List Permissions for a repository.
    :ivar created_on: Time the repository was created
    :vartype created_on: Optional[~datetime.datetime]
    :ivar last_updated_on: Time the repository was last updated.
    :vartype last_updated_on: Optional[~datetime.datetime]
    :ivar Optional[int] manifest_count: Number of manifest in the repository.
    :ivar Optional[str] name: Name of the repository.
    :ivar Optional[int] tag_count: Number of tags associated with the repository.
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

    def __getattr__(self, name):
        if name == "last_udpated_on":
            warnings.warn(
                "The property name with a typo called 'last_udpated_on' has been deprecated and will be retired in future versions", # pylint: disable=line-too-long
                DeprecationWarning)
            return self.last_updated_on
        return super().__getattr__(self, name) # pylint: disable=no-member

    @property
    def created_on(self) -> datetime:
        return self._created_on

    @property
    def last_updated_on(self) -> datetime:
        return self._last_updated_on

    @property
    def manifest_count(self) -> int:
        return self._manifest_count

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag_count(self) -> int:
        return self._tag_count


class ArtifactTagProperties(object):
    """Represents properties of a single tag

    :ivar bool can_delete: Delete Permissions for a tag.
    :ivar bool can_write: Write Permissions for a tag.
    :ivar bool can_read: Read Permissions for a tag.
    :ivar bool can_list: List Permissions for a tag.
    :ivar created_on: Time the tag was created.
    :vartype created_on: Optional[~datetime.datetime]
    :ivar Optional[str] digest: Digest for the tag.
    :ivar last_updated_on: Time the tag was last updated.
    :vartype last_updated_on: Optional[~datetime.datetime]
    :ivar Optional[str] name: Name of the image the tag corresponds to.
    :ivar Optional[str] repository_name: Repository name the tag belongs to.
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
            repository_name=kwargs.get("repository_name", None),
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
        return self._created_on

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def last_updated_on(self) -> datetime:
        return self._last_updated_on

    @property
    def name(self) -> str:
        return self._name

    @property
    def repository_name(self) -> str:
        return self._repository_name


class GetManifestResult(object):
    """The get manifest result.

    :ivar dict manifest: The manifest JSON.
    :ivar str media_type: The manifest's media type.
    :ivar str digest: The manifest's digest, calculated by the registry.
    """

    def __init__(self, **kwargs):
        self.manifest = kwargs.get("manifest")
        self.media_type = kwargs.get("media_type")
        self.digest = kwargs.get("digest")


class ManifestDigestValidationError(ValueError):
    """Thrown when a manifest digest validation fails.
    :param str message: Message for caller describing the reason for the failure.
    """

    def __init__(self, message):
        self.message = message
        super(  # pylint: disable=super-with-arguments
            ManifestDigestValidationError, self
        ).__init__(self.message)
