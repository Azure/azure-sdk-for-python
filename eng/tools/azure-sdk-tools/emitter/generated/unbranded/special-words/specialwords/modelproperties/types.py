# coding=utf-8

from typing_extensions import Required, TypedDict


class DictMethods(TypedDict, total=False):
    """DictMethods.

    :ivar keys_property: Required.
    :vartype keys_property: str
    :ivar items_property: Required.
    :vartype items_property: str
    :ivar values_property: Required.
    :vartype values_property: str
    :ivar popitem_property: Required.
    :vartype popitem_property: str
    :ivar clear_property: Required.
    :vartype clear_property: str
    :ivar update_property: Required.
    :vartype update_property: str
    :ivar setdefault_property: Required.
    :vartype setdefault_property: str
    :ivar pop_property: Required.
    :vartype pop_property: str
    :ivar get_property: Required.
    :vartype get_property: str
    :ivar copy_property: Required.
    :vartype copy_property: str
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

    :ivar same_as_model: Required.
    :vartype same_as_model: str
    """

    SameAsModel: Required[str]
    """Required."""
