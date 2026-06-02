# coding=utf-8

from typing_extensions import Required, TypedDict


class Element(TypedDict, total=False):
    """element.

    :ivar extension:
    :vartype extension: list[~typetest.model.recursive.models.Extension]
    """

    extension: list["Extension"]


class Extension(Element):
    """extension.

    :ivar extension:
    :vartype extension: list[~typetest.model.recursive.models.Extension]
    :ivar level: Required.
    :vartype level: int
    """

    level: Required[int]
    """Required."""
