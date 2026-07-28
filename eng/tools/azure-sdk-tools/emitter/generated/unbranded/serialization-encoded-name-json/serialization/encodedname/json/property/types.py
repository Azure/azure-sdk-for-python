# coding=utf-8

from typing_extensions import Required, TypedDict


class JsonEncodedNameModel(TypedDict, total=False):
    """JsonEncodedNameModel.

    :ivar wireName: Pass in true. Required.
    :vartype wireName: bool
    """

    wireName: Required[bool]
    """Pass in true. Required."""
