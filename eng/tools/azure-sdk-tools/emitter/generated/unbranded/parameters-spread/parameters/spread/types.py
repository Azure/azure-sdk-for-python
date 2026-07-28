# coding=utf-8

from typing_extensions import Required, TypedDict


class SpreadCompositeRequestMixRequest(TypedDict, total=False):
    """SpreadCompositeRequestMixRequest.

    :ivar prop: Required.
    :vartype prop: str
    """

    prop: Required[str]
    """Required."""


class SpreadParameterWithInnerModelRequest(TypedDict, total=False):
    """SpreadParameterWithInnerModelRequest.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""


class SpreadAsRequestParameterRequest(TypedDict, total=False):
    """SpreadAsRequestParameterRequest.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""


class SpreadWithMultipleParametersRequest(TypedDict, total=False):
    """SpreadWithMultipleParametersRequest.

    :ivar requiredString: required string. Required.
    :vartype requiredString: str
    :ivar optionalInt: optional int.
    :vartype optionalInt: int
    :ivar requiredIntList: required int. Required.
    :vartype requiredIntList: list[int]
    :ivar optionalStringList: optional string.
    :vartype optionalStringList: list[str]
    """

    requiredString: Required[str]
    """required string. Required."""
    optionalInt: int
    """optional int."""
    requiredIntList: Required[list[int]]
    """required int. Required."""
    optionalStringList: list[str]
    """optional string."""


class SpreadParameterWithInnerAliasRequest(TypedDict, total=False):
    """SpreadParameterWithInnerAliasRequest.

    :ivar name: name of the Thing. Required.
    :vartype name: str
    :ivar age: age of the Thing. Required.
    :vartype age: int
    """

    name: Required[str]
    """name of the Thing. Required."""
    age: Required[int]
    """age of the Thing. Required."""
