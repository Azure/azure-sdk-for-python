# coding=utf-8

from typing_extensions import Required, TypedDict

from ._utils.utils import FileType


class Address(TypedDict, total=False):
    """Address.

    :ivar city: Required.
    :vartype city: str
    """

    city: Required[str]
    """Required."""


class BinaryArrayPartsRequest(TypedDict, total=False):
    """BinaryArrayPartsRequest.

    :ivar id: Required.
    :vartype id: str
    :ivar pictures: Required.
    :vartype pictures: list[FileType]
    """

    id: Required[str]
    """Required."""
    pictures: Required[list[FileType]]
    """Required."""


class ComplexHttpPartsModelRequest(TypedDict, total=False):
    """ComplexHttpPartsModelRequest.

    :ivar id: Required.
    :vartype id: str
    :ivar address: Required.
    :vartype address: "Address"
    :ivar profileImage: Required.
    :vartype profileImage: FileType
    :ivar previousAddresses: Required.
    :vartype previousAddresses: list["Address"]
    :ivar pictures: Required.
    :vartype pictures: list[FileType]
    """

    id: Required[str]
    """Required."""
    address: Required["Address"]
    """Required."""
    profileImage: Required[FileType]
    """Required."""
    previousAddresses: Required[list["Address"]]
    """Required."""
    pictures: Required[list[FileType]]
    """Required."""


class ComplexPartsRequest(TypedDict, total=False):
    """ComplexPartsRequest.

    :ivar id: Required.
    :vartype id: str
    :ivar address: Required.
    :vartype address: "Address"
    :ivar profileImage: Required.
    :vartype profileImage: FileType
    :ivar pictures: Required.
    :vartype pictures: list[FileType]
    """

    id: Required[str]
    """Required."""
    address: Required["Address"]
    """Required."""
    profileImage: Required[FileType]
    """Required."""
    pictures: Required[list[FileType]]
    """Required."""


class FileWithHttpPartOptionalContentTypeRequest(TypedDict, total=False):  # pylint: disable=name-too-long
    """FileWithHttpPartOptionalContentTypeRequest.

    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    profileImage: Required[FileType]
    """Required."""


class FileWithHttpPartRequiredContentTypeRequest(TypedDict, total=False):  # pylint: disable=name-too-long
    """FileWithHttpPartRequiredContentTypeRequest.

    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    profileImage: Required[FileType]
    """Required."""


class FileWithHttpPartSpecificContentTypeRequest(TypedDict, total=False):  # pylint: disable=name-too-long
    """FileWithHttpPartSpecificContentTypeRequest.

    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    profileImage: Required[FileType]
    """Required."""


class JsonPartRequest(TypedDict, total=False):
    """JsonPartRequest.

    :ivar address: Required.
    :vartype address: "Address"
    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    address: Required["Address"]
    """Required."""
    profileImage: Required[FileType]
    """Required."""


class MultiBinaryPartsRequest(TypedDict, total=False):
    """MultiBinaryPartsRequest.

    :ivar profileImage: Required.
    :vartype profileImage: FileType
    :ivar picture:
    :vartype picture: FileType
    """

    profileImage: Required[FileType]
    """Required."""
    picture: FileType


class MultiPartOptionalRequest(TypedDict, total=False):
    """MultiPartOptionalRequest.

    :ivar id:
    :vartype id: str
    :ivar profileImage:
    :vartype profileImage: FileType
    """

    id: str
    profileImage: FileType


class MultiPartRequest(TypedDict, total=False):
    """MultiPartRequest.

    :ivar id: Required.
    :vartype id: str
    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    id: Required[str]
    """Required."""
    profileImage: Required[FileType]
    """Required."""


class MultiPartRequestWithWireName(TypedDict, total=False):
    """MultiPartRequestWithWireName.

    :ivar id: Required.
    :vartype id: str
    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    id: Required[str]
    """Required."""
    profileImage: Required[FileType]
    """Required."""
