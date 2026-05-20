# coding=utf-8

from typing import Optional, TYPE_CHECKING
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from ...types import Pet


class RequestHeaderNestedResponseBodyResponseNestedItems(TypedDict, total=False):  # pylint: disable=name-too-long
    """RequestHeaderNestedResponseBodyResponseNestedItems.

    :ivar pets: Required.
    :vartype pets: list[~payload.pageable.models.Pet]
    """

    pets: Required[list["Pet"]]
    """Required."""


class RequestHeaderNestedResponseBodyResponseNestedNext(TypedDict, total=False):  # pylint: disable=name-too-long
    """RequestHeaderNestedResponseBodyResponseNestedNext.

    :ivar next_token:
    :vartype next_token: str
    """

    nextToken: Optional[str]


class RequestQueryNestedResponseBodyResponseNestedItems(TypedDict, total=False):  # pylint: disable=name-too-long
    """RequestQueryNestedResponseBodyResponseNestedItems.

    :ivar pets: Required.
    :vartype pets: list[~payload.pageable.models.Pet]
    """

    pets: Required[list["Pet"]]
    """Required."""


class RequestQueryNestedResponseBodyResponseNestedNext(TypedDict, total=False):  # pylint: disable=name-too-long
    """RequestQueryNestedResponseBodyResponseNestedNext.

    :ivar next_token:
    :vartype next_token: str
    """

    nextToken: Optional[str]
