# coding=utf-8

from typing import Literal, Optional, Union
from typing_extensions import Required, TypedDict


class Eagle(TypedDict, total=False):
    """The second level model in polymorphic single levels inheritance which contains references to
    other polymorphic instances.

    :ivar wingspan: Required.
    :vartype wingspan: int
    :ivar kind: Required. Default value is "eagle".
    :vartype kind: str
    :ivar friends:
    :vartype friends: list[~typetest.model.singlediscriminator.models.Bird]
    :ivar hate:
    :vartype hate: dict[str, ~typetest.model.singlediscriminator.models.Bird]
    :ivar partner:
    :vartype partner: ~typetest.model.singlediscriminator.models.Bird
    """

    wingspan: Required[int]
    """Required."""
    kind: Required[Literal["eagle"]]
    """Required. Default value is \"eagle\"."""
    friends: Optional[list["Bird"]]
    hate: Optional[dict[str, "Bird"]]
    partner: Optional["Bird"]


class Goose(TypedDict, total=False):
    """The second level model in polymorphic single level inheritance.

    :ivar wingspan: Required.
    :vartype wingspan: int
    :ivar kind: Required. Default value is "goose".
    :vartype kind: str
    """

    wingspan: Required[int]
    """Required."""
    kind: Required[Literal["goose"]]
    """Required. Default value is \"goose\"."""


class SeaGull(TypedDict, total=False):
    """The second level model in polymorphic single level inheritance.

    :ivar wingspan: Required.
    :vartype wingspan: int
    :ivar kind: Required. Default value is "seagull".
    :vartype kind: str
    """

    wingspan: Required[int]
    """Required."""
    kind: Required[Literal["seagull"]]
    """Required. Default value is \"seagull\"."""


class Sparrow(TypedDict, total=False):
    """The second level model in polymorphic single level inheritance.

    :ivar wingspan: Required.
    :vartype wingspan: int
    :ivar kind: Required. Default value is "sparrow".
    :vartype kind: str
    """

    wingspan: Required[int]
    """Required."""
    kind: Required[Literal["sparrow"]]
    """Required. Default value is \"sparrow\"."""


class TRex(TypedDict, total=False):
    """The second level legacy model in polymorphic single level inheritance.

    :ivar size: Required.
    :vartype size: int
    :ivar kind: Required. Default value is "t-rex".
    :vartype kind: str
    """

    size: Required[int]
    """Required."""
    kind: Required[Literal["t-rex"]]
    """Required. Default value is \"t-rex\"."""


Bird = Union[Eagle, Goose, SeaGull, Sparrow]
Dinosaur = Union[TRex]
