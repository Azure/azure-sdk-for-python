# coding=utf-8

from typing_extensions import Required, TypedDict


class Pet(TypedDict, total=False):
    """Pet.

    :ivar id: Required.
    :vartype id: str
    :ivar name: Required.
    :vartype name: str
    """

    id: Required[str]
    """Required."""
    name: Required[str]
    """Required."""


class XmlPet(TypedDict, total=False):
    """An XML pet item.

    :ivar id: Required.
    :vartype id: str
    :ivar name: Required.
    :vartype name: str
    """

    id: Required[str]
    """Required."""
    name: Required[str]
    """Required."""
