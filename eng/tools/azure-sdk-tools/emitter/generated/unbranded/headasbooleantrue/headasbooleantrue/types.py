# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class ReadOnlyModel(TypedDict, total=False):
    """RoundTrip model with readonly optional properties.

    :ivar optional_nullable_int_list: Optional readonly nullable int list.
    :vartype optional_nullable_int_list: list[int]
    :ivar optional_string_record: Optional readonly string dictionary.
    :vartype optional_string_record: dict[str, str]
    """

    optionalNullableIntList: Optional[list[int]]
    """Optional readonly nullable int list."""
    optionalStringRecord: Optional[dict[str, str]]
    """Optional readonly string dictionary."""


class VisibilityModel(TypedDict, total=False):
    """Output model with visibility properties.

    :ivar read_prop: Required string, illustrating a readonly property. Required.
    :vartype read_prop: str
    :ivar create_prop: Required string[], illustrating a create property. Required.
    :vartype create_prop: list[str]
    :ivar update_prop: Required int32[], illustrating a update property. Required.
    :vartype update_prop: list[int]
    :ivar delete_prop: Required bool, illustrating a delete property. Required.
    :vartype delete_prop: bool
    """

    readProp: Required[str]
    """Required string, illustrating a readonly property. Required."""
    createProp: Required[list[str]]
    """Required string[], illustrating a create property. Required."""
    updateProp: Required[list[int]]
    """Required int32[], illustrating a update property. Required."""
    deleteProp: Required[bool]
    """Required bool, illustrating a delete property. Required."""
