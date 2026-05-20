# coding=utf-8

from typing_extensions import Required, TypedDict

from ..._utils.utils import FileType


class UploadFileArrayRequest(TypedDict, total=False):
    """UploadFileArrayRequest.

    :ivar files: Required.
    :vartype files: list[~payload.multipart._utils.utils.FileType]
    """

    files: Required[list[FileType]]
    """Required."""


class UploadFileRequiredFilenameRequest(TypedDict, total=False):
    """UploadFileRequiredFilenameRequest.

    :ivar file: Required.
    :vartype file: ~payload.multipart._utils.utils.FileType
    """

    file: Required[FileType]
    """Required."""


class UploadFileSpecificContentTypeRequest(TypedDict, total=False):
    """UploadFileSpecificContentTypeRequest.

    :ivar file: Required.
    :vartype file: ~payload.multipart._utils.utils.FileType
    """

    file: Required[FileType]
    """Required."""
