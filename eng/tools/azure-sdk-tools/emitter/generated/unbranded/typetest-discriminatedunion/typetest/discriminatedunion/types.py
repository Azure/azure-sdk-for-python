# coding=utf-8

from typing_extensions import Required, TypedDict


class Cat(TypedDict, total=False):
    """Cat.

    :ivar name: Required.
    :vartype name: str
    :ivar meow: Required.
    :vartype meow: bool
    """

    name: Required[str]
    """Required."""
    meow: Required[bool]
    """Required."""


class Dog(TypedDict, total=False):
    """Dog.

    :ivar name: Required.
    :vartype name: str
    :ivar bark: Required.
    :vartype bark: bool
    """

    name: Required[str]
    """Required."""
    bark: Required[bool]
    """Required."""
