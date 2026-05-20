# coding=utf-8

from typing_extensions import Required, TypedDict


class JsonEncodedNameModel(TypedDict, total=False):
    """JsonEncodedNameModel.

    :ivar default_name: Pass in true. Required.
    :vartype default_name: bool
    """

    wireName: Required[bool]
    """Pass in true. Required."""
