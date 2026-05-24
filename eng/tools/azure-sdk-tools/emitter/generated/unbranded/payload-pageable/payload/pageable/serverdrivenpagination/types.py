# coding=utf-8

from typing import Optional, TYPE_CHECKING
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from ..types import Pet


class NestedLinkResponseNestedItems(TypedDict, total=False):
    """NestedLinkResponseNestedItems.

    :ivar pets: Required.
    :vartype pets: list[~payload.pageable.models.Pet]
    """

    pets: Required[list["Pet"]]
    """Required."""


class NestedLinkResponseNestedNext(TypedDict, total=False):
    """NestedLinkResponseNestedNext.

    :ivar next:
    :vartype next: str
    """

    next: Optional[str]
