# coding=utf-8

from typing_extensions import Required, TypedDict


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


class NestedParameterBody(TypedDict, total=False):
    """NestedParameterBody.

    :ivar bodyRootParameters: Required.
    :vartype bodyRootParameters: "BodyRootModel"
    """

    bodyRootParameters: Required["BodyRootModel"]
    """Required."""
