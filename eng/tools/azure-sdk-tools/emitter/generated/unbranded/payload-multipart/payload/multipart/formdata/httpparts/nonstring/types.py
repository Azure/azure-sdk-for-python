# coding=utf-8

from typing_extensions import Required, TypedDict


class FloatRequest(TypedDict, total=False):
    """FloatRequest.

    :ivar temperature: Required.
    :vartype temperature: float
    """

    temperature: Required[float]
    """Required."""
