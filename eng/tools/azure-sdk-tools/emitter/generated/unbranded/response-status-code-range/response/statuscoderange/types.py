# coding=utf-8

from typing_extensions import Required, TypedDict


class DefaultError(TypedDict, total=False):
    """DefaultError.

    :ivar code: Required.
    :vartype code: str
    """

    code: Required[str]
    """Required."""


class ErrorInRange(TypedDict, total=False):
    """ErrorInRange.

    :ivar code: Required.
    :vartype code: str
    :ivar message: Required.
    :vartype message: str
    """

    code: Required[str]
    """Required."""
    message: Required[str]
    """Required."""


class NotFoundError(TypedDict, total=False):
    """NotFoundError.

    :ivar code: Required.
    :vartype code: str
    :ivar resource_id: Required.
    :vartype resource_id: str
    """

    code: Required[str]
    """Required."""
    resourceId: Required[str]
    """Required."""


class Standard4XXError(TypedDict, total=False):
    """Standard4XXError.

    :ivar code: Required.
    :vartype code: str
    """

    code: Required[str]
    """Required."""
