# coding=utf-8

from typing_extensions import Required, TypedDict


class DictMethods(TypedDict, total=False):
    """DictMethods.

    :ivar keys: Required.
    :vartype keys: str
    :ivar items: Required.
    :vartype items: str
    :ivar values: Required.
    :vartype values: str
    :ivar popitem: Required.
    :vartype popitem: str
    :ivar clear: Required.
    :vartype clear: str
    :ivar update: Required.
    :vartype update: str
    :ivar setdefault: Required.
    :vartype setdefault: str
    :ivar pop: Required.
    :vartype pop: str
    :ivar get: Required.
    :vartype get: str
    :ivar copy: Required.
    :vartype copy: str
    """

    keys: Required[str]
    """Required."""
    items: Required[str]
    """Required."""
    values: Required[str]
    """Required."""
    popitem: Required[str]
    """Required."""
    clear: Required[str]
    """Required."""
    update: Required[str]
    """Required."""
    setdefault: Required[str]
    """Required."""
    pop: Required[str]
    """Required."""
    get: Required[str]
    """Required."""
    copy: Required[str]
    """Required."""


class ModelWithList(TypedDict, total=False):
    """ModelWithList.

    :ivar list: Required.
    :vartype list: str
    """

    list: Required[str]
    """Required."""


class SameAsModel(TypedDict, total=False):
    """SameAsModel.

    :ivar SameAsModel: Required.
    :vartype SameAsModel: str
    """

    SameAsModel: Required[str]
    """Required."""
