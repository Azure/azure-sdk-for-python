# coding=utf-8

from typing_extensions import Required, TypedDict


class Pet(TypedDict, total=False):
    """This is base model for not-discriminated normal multiple levels inheritance.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""


class Cat(Pet):
    """The second level model in the normal multiple levels inheritance.

    :ivar name: Required.
    :vartype name: str
    :ivar age: Required.
    :vartype age: int
    """

    age: Required[int]
    """Required."""


class Siamese(Cat):
    """The third level model in the normal multiple levels inheritance.

    :ivar name: Required.
    :vartype name: str
    :ivar age: Required.
    :vartype age: int
    :ivar smart: Required.
    :vartype smart: bool
    """

    smart: Required[bool]
    """Required."""
