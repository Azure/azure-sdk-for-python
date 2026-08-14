# coding=utf-8

from typing_extensions import TypedDict


class BodyRootModel(TypedDict, total=False):
    """BodyRootModel.

    :ivar category:
    :vartype category: str
    :ivar linkType:
    :vartype linkType: str
    :ivar wasSuccessful:
    :vartype wasSuccessful: bool
    """

    category: str
    linkType: str
    wasSuccessful: bool
