# coding=utf-8

from typing import Optional
from typing_extensions import Required, TypedDict


class InnerModel(TypedDict, total=False):
    """Dictionary inner model.

    :ivar property: Required string property. Required.
    :vartype property: str
    :ivar children:
    :vartype children: dict[str, ~typetest.dictionary.models.InnerModel]
    """

    property: Required[str]
    """Required string property. Required."""
    children: Optional[dict[str, "InnerModel"]]
