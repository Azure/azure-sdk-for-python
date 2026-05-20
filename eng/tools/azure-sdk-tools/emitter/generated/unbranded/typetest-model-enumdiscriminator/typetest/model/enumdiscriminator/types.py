# coding=utf-8

from typing import Literal, Union
from typing_extensions import Required, TypedDict

from .models._enums import DogKind, SnakeKind


class Cobra(TypedDict, total=False):
    """Cobra model.

    :ivar length: Length of the snake. Required.
    :vartype length: int
    :ivar kind: discriminator property. Required. Species cobra.
    :vartype kind: str or ~typetest.model.enumdiscriminator.models.COBRA
    """

    length: Required[int]
    """Length of the snake. Required."""
    kind: Required[Literal[SnakeKind.COBRA]]
    """discriminator property. Required. Species cobra."""


class Golden(TypedDict, total=False):
    """Golden dog model.

    :ivar weight: Weight of the dog. Required.
    :vartype weight: int
    :ivar kind: discriminator property. Required. Species golden.
    :vartype kind: str or ~typetest.model.enumdiscriminator.models.GOLDEN
    """

    weight: Required[int]
    """Weight of the dog. Required."""
    kind: Required[Literal[DogKind.GOLDEN]]
    """discriminator property. Required. Species golden."""


Snake = Union[Cobra]
Dog = Union[Golden]
