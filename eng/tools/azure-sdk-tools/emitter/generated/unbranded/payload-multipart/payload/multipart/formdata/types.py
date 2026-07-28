# coding=utf-8

from typing_extensions import Required, TypedDict

from .._utils.utils import FileType


class AnonymousModelRequest(TypedDict, total=False):
    """AnonymousModelRequest.

    :ivar profileImage: Required.
    :vartype profileImage: FileType
    """

    profileImage: Required[FileType]
    """Required."""
