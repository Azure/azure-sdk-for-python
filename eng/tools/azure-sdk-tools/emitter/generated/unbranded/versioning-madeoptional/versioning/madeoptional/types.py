# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class TestModel(TypedDict, total=False):
    """TestModel.

    :ivar prop: Required.
    :vartype prop: str
    :ivar changed_prop:
    :vartype changed_prop: str
    """

    prop: Required[str]
    """Required."""
    changedProp: Optional[str]
