# coding=utf-8

from typing_extensions import Required, TypedDict


class BoolAsStringProperty(TypedDict, total=False):
    """BoolAsStringProperty.

    :ivar value: Required.
    :vartype value: bool
    """

    value: Required[bool]
    """Required."""
